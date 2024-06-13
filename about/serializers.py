from rest_framework import serializers

from about.models import FAQ, Feedback


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            "question",
            "answer"
        ]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "info"
        ]
