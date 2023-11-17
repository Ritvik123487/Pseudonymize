def reidentify(request):
    
    #Note refer to logger per part for some more detials on each block of code
    import logging
    from django.http import HttpResponse
    from google.cloud import storage
    from google.cloud import dlp
    import json
    import csv
    import io

    # Get an instance of a logger
    logger = logging.getLogger(__name__)
    logger.debug("Starting reidentify process")

    # Initialize the DLP client
    dlp_client = dlp.DlpServiceClient()
    logger.debug("DLP client initialized")

    # Creds
    parent = 'projects/pii-software'
    reidentify_template_name = "projects/pii-software/deidentifyTemplates/5626449971329233065"
    source_bucket_name = 'dataaccel-bucket-pseudonymized'
    source_file_name = request.POST.get('source_file_name')
    if source_file_name is None:
        logger.error("No source_file_name provided in POST request")
        return HttpResponse("No source_file_name provided", status=400)

    storage_client = storage.Client()
    logger.debug("GCS client initialized")

    # Get the source bucket and blob reference
    source_bucket = storage_client.bucket(source_bucket_name)
    source_blob = source_bucket.blob(source_file_name)

    file_content = source_blob.download_as_bytes().decode('utf-8')
    logger.debug("File content downloaded")

    if source_file_name.endswith(".csv"):
        csv_reader = csv.reader(io.StringIO(file_content))
        rows = list(csv_reader)
        headers = [{'name': header} for header in rows[0]]
        rows = [{'values': [{'string_value': cell} for cell in row]} for row in rows[1:]]
        item = {'table': {'headers': headers, 'rows': rows}}
    elif source_file_name.endswith(".json"):
        item = {'value': json.dumps(json.loads(file_content))}
    else:
        logger.error(f"Unsupported file type: {source_file_name}")
        return HttpResponse(f"Unsupported file type: {source_file_name}", status=400)
    logger.debug("File parsed into table object")

    response = dlp_client.reidentify_content(
        request={
            "parent": parent,
            "reidentify_template_name": reidentify_template_name,
            "item": item
        }
    )
    logger.debug("DLP reidentify_content called")

    if source_file_name.endswith(".csv"):
        reidentified_text = ",".join([header.name for header in response.item.table.headers]) + "\n"
        reidentified_text += "\n".join([",".join([cell.string_value for cell in row.values]) for row in response.item.table.rows])
    elif source_file_name.endswith(".json"):
        reidentified_text = response.item.value
    logger.debug("Reidentified table converted back to original format")

    # Allow download to browser
    response = HttpResponse(reidentified_text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={source_file_name}'
    logger.debug("Response created with Content-Disposition header set to 'attachment'")

    return response
