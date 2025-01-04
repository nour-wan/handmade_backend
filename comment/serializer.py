from .models import Comment
from rest_framework import serializers

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    def to_array(comment):
        array = []
        for arr in comment:
            json = {
                "id": arr.id,
                "customer" : arr.customer.id,
                "customer_name" : arr.customer.user.username,
                "handcraft" : arr.handcraft.id,
                "date" : arr.date,
                "time" : arr.time,
                "description" : arr.description,
            }
            array.append(json)
        return array     

    def get_comment(comment):
        json = {
            "id": comment.id,
            "customer" : comment.customer.id,
            "customer_name" : comment.customer.user.username,
            "handcraft" : comment.handcraft.id,
            "date" : comment.date,
            "time" : comment.time,
            "description" : comment.description,
        }
        return json