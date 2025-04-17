from rest_framework import serializers

class CleanedImageURLField(serializers.ImageField):
    def to_representation(self, value):
        request = self.context.get('request')
        if request and value:
            full_url = request.build_absolute_uri(value.url)
            path_prefix = request.path.split('/')[1]  # يأخذ أول جزء من URL مثل 'auctions'
            return full_url.replace(f'/{path_prefix}', '', 1)
        return super().to_representation(value)