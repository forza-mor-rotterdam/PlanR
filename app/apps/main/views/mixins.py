from django.views.generic import View


class StreamViewMixin(View):
    is_stream = True

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        response.headers["Content-Type"] = "text/vnd.turbo-stream.html"
        return response
