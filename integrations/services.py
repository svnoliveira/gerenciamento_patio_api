# integrations/services.py
from django.db import transaction
from companies.models import Company
from trucks.models import Truck

REQUIRED_FIELDS = [
    "company_name",
    "plate",
    "driver",
    "cpf",
    "cellphone",
    "product",
    "type",
]


def validate_row(row: dict, row_number: int) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if not row.get(field):
            errors.append(
                f"Linha {row_number}: campo obrigatório ausente ou vazio: '{field}'"
            )
    return errors


@transaction.atomic
def upsert_rows(rows: list[dict]) -> dict:

    created_companies = 0
    created_trucks = 0
    updated_trucks = 0
    errors = []

    for index, row in enumerate(rows, start=2):
        row_errors = validate_row(row, index)
        if row_errors:
            errors.extend(row_errors)
            continue

        try:
            company, was_created = Company.objects.get_or_create(
                name=row["company_name"].strip()
            )
            if was_created:
                created_companies += 1

            truck_defaults = {
                "company": company,
                "driver": row["driver"],
                "cpf": row["cpf"],
                "cellphone": row["cellphone"],
                "product": row["product"],
                "type": row["type"],
                "granel": row.get("granel") or None,
                "bag": row.get("bag") or None,
                "pallet": row.get("pallet") or None,
            }

            truck, was_created = Truck.objects.update_or_create(
                plate=row["plate"].strip().upper(),
                defaults=truck_defaults,
            )

            if was_created:
                created_trucks += 1
            else:
                updated_trucks += 1

        except Exception as e:
            errors.append(f"Linha {index}: erro ao processar - {str(e)}")

    return {
        "created_companies": created_companies,
        "created_trucks": created_trucks,
        "updated_trucks": updated_trucks,
        "errors": errors,
        "total_rows": len(rows),
    }
