from .models import Rating
from rest_framework import serializers

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

    def rating_by_handcraft(rating):
        # serializer = RatingSerializer(rating, many = True)
        total_stars = 0
        for ser in rating:
           total_stars =  total_stars + ser.stars
        print(total_stars)
        total_count = rating.count()
        print(total_count)
        if total_count == 0 :
            return 0
        total = total_stars / total_count
        print(total) 
        return total   



        