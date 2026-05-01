class LogginMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self,request):
        print(f"{request.META.get('HTTP_HOST')}/verify/")

        response = self.get_response(request)
        print(response.status_code)

        return response