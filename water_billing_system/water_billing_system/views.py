from django.shortcuts import render
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def custom_permission_denied_view(request, exception):
    logger.warning(f'Permission denied: {request.path} - {exception}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    return render(request, '403.html', status=403)

def custom_page_not_found_view(request, exception):
    logger.warning(f'Page not found: {request.path} - {exception}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Page not found'}, status=404)
    return render(request, '404.html', status=404)

def custom_error_view(request):
    logger.error(f'Server error: {request.path}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Server error'}, status=500)
    return render(request, '500.html', status=500)