import os
from rest_framework import serializers

ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}
MAX_DOCUMENT_SIZE_BYTES = 20 * 1024 * 1024


def validate_document_upload(file):
    if file is None:
        return file
    if file.size > MAX_DOCUMENT_SIZE_BYTES:
        raise serializers.ValidationError("O arquivo não pode ser maior que 20 MB.")
    if os.path.splitext(file.name)[1].lower() not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise serializers.ValidationError(
            "Tipo de arquivo não permitido. Use PDF, DOC, DOCX ou TXT."
        )
    return file
