from corsheaders.signals import check_request_enabled


def cors_allow_api_to_all_360(sender, request, **kwargs):
    if request.path.startswith("/api/"):
        if "Origin" in request.headers:
            if request.headers["Origin"].endswith(".threesixtygiving.org"):
                return True
    return False


check_request_enabled.connect(cors_allow_api_to_all_360)
