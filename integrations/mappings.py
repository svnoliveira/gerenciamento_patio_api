# integrations/mappings.py


EXCEL_COLUMN_MAP = {
    "Empresa": "company_name",
    "Placa": "plate",
    "Motorista": "driver",
    "CPF": "cpf",
    "Telefone": "cellphone",
    "Produto": "product",
    "Tipo": "type",
    "Granel": "granel",
    "Bag": "bag",
    "Pallet": "pallet",
}


API_FIELD_MAP = {
    "empresa_nome": "company_name",
    "placa_veiculo": "plate",
    "nome_motorista": "driver",
    "cpf_motorista": "cpf",
    "telefone": "cellphone",
    "produto": "product",
    "tipo_veiculo": "type",
    "qtd_granel": "granel",
    "qtd_bag": "bag",
    "qtd_pallet": "pallet",
}


def remap_row(raw_row: dict, field_map: dict) -> dict:
    result = {}
    for source_key, target_key in field_map.items():
        if source_key in raw_row:
            result[target_key] = raw_row[source_key]
    return result
