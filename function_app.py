import azure.functions as func
import logging
import requests
import json

app = func.FunctionApp()


@app.route(route="open311_api", auth_level=func.AuthLevel.ANONYMOUS)
def open311_api(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('open311 HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError as e:
        return func.HttpResponse(f'Invalid or missing JSON body.\n{e}', status_code=400)

    url = req_body.get('url', 'https://austin2-production.spotmobile.net/open311/v2/requests.json')
    sr_code = req_body.get('service_code', "PARKINGV")
    page_size = req_body.get('page_size', 100)
    page = req_body.get('page')
    start_date = req_body.get('start_date')
    end_date = req_body.get('end_date')
    extensions = req_body.get('extensions', "true")

    if not page or not start_date or not end_date:
        return func.HttpResponse(f"Missing required json fields for page, start_date, or end_date.", status_code=400)

    parameters = {
        "extensions": extensions,
        "page_size": page_size,
        "service_code": sr_code,
        "page": page,
        "start_date": start_date,
        "end_date": end_date,
    }

    result = requests.get(url, params=parameters)

    if result.status_code != 200:
        return func.HttpResponse(f'Request to open311 failed.\n{result.text}', status_code=result.status_code)

    data = result.json()
    logging.info(f"data: {data}")
    logging.info(result.text)
    response_body = {
        "result_count": len(data)
    }

    return func.HttpResponse(
        json.dumps(response_body),
        status_code=200
    )
