from django.shortcuts import render


def csrf_failure(request, reason=''):
    return render(request, 'pages/errs/403csrf.html', status=403)


def access_denied(request, exception):
    return render(request, 'pages/errs/403.html', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/errs/404.html', status=404)


def internal_server(request):
    return render(request, 'pages/errs/500.html', status=500)
