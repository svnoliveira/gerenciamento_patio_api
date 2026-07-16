import requests
import openpyxl
from rest_framework.views import APIView
from rest_framework.response import Response

# from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.conf import settings
from _core.permissions import IsSuperUserOrSafeMethod
from .mappings import API_FIELD_MAP, EXCEL_COLUMN_MAP, remap_row
from .services import upsert_rows


class ExcelImportView(APIView):
    permission_classes = [IsSuperUserOrSafeMethod]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"detail": "Nenhum arquivo enviado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            workbook = openpyxl.load_workbook(file, data_only=True)
            sheet = workbook.active
        except Exception:
            return Response(
                {
                    "detail": (
                        "Não foi possível ler o arquivo. "
                        "Verifique se é um .xlsx válido."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        rows_iter = sheet.iter_rows(values_only=True)
        headers = next(rows_iter, None)
        if not headers:
            return Response(
                {"detail": "Planilha vazia."}, status=status.HTTP_400_BAD_REQUEST
            )

        raw_rows = []
        for row_values in rows_iter:
            if all(v is None for v in row_values):
                continue
            raw_row = dict(zip(headers, row_values))
            raw_rows.append(remap_row(raw_row, EXCEL_COLUMN_MAP))

        result = upsert_rows(raw_rows)
        return Response(result)


class ExternalApiSyncView(APIView):
    permission_classes = [IsSuperUserOrSafeMethod]

    def post(self, request):
        api_url = getattr(settings, "FINANCIAL_API_URL", None)
        api_key = getattr(settings, "FINANCIAL_API_KEY", None)

        if not api_url or not api_key:
            return Response(
                {"detail": "Integração externa ainda não configurada."},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        try:
            resp = requests.get(
                api_url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            raw_data = resp.json()
        except requests.RequestException as e:
            return Response(
                {"detail": f"Erro ao buscar dados da API externa: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # NOTE: adjust with the real response shape
        # (likely raw_data["results"] or similar)
        raw_rows = (
            raw_data if isinstance(raw_data, list) else raw_data.get("results", [])
        )
        mapped_rows = [remap_row(row, API_FIELD_MAP) for row in raw_rows]

        result = upsert_rows(mapped_rows)
        return Response(result)
