from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.serializers import PasswordChangeSerializer

from client.serializers import UserSerializer, MeSerializer
from client.models import User
from service.serializers import ScheduleRetrieveSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            return MeSerializer
        elif self.action == "list":
            return UserSerializer
        elif self.action == "schedule":
            return ScheduleRetrieveSerializer
        elif self.action == "password":
            return PasswordChangeSerializer
        return self.serializer_class

    def get_object(self):
        return self.request.user

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated]
    )
    def schedule(self, request):
        user = self.request.user
        bookings = user.users.all().select_related()
        serializer = self.get_serializer(bookings, many=True)
        return Response(
            {"schedule": serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["PUT", "PATCH"])
    def password(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"status": "password set"}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except KeyError:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
