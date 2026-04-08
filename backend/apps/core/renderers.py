"""
Custom API response renderer for consistent response envelope.

All API responses follow this structure:
{
    "status": "success" | "error",
    "message": "...",
    "data": {...} | [...],
    "meta": {...}   # pagination info, etc.
}
"""
import json
from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        status_code = response.status_code if response else 200

        # Determine success/error from status code
        is_success = 200 <= status_code < 400

        # Handle paginated responses (they have 'results' key)
        if isinstance(data, dict) and 'results' in data:
            envelope = {
                'status': 'success',
                'data': data.get('results', []),
                'meta': {
                    'count': data.get('count', 0),
                    'next': data.get('next'),
                    'previous': data.get('previous'),
                },
            }
        elif is_success:
            envelope = {
                'status': 'success',
                'data': data,
            }
        else:
            # Error response
            envelope = {
                'status': 'error',
                'errors': data,
            }

        return super().render(envelope, accepted_media_type, renderer_context)
