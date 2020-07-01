from rest_framework import mixins, viewsets, status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from API_admin import serializers as serial
from seance.models import SeatCategory, Price, Film, Hall


class ViewSetInsert:
    permission_classes = (IsAdminUser,)

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

    def perform_update(self, serializer):
        serializer.save(admin=self.request.user)


class SeatCategoryViewSet(ViewSetInsert, viewsets.ModelViewSet):
    queryset = SeatCategory.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.SeatCategoryHyperSerializer
        else:
            return serial.SeatCategoryCUDSerializer


class PriceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = serial.PriceHyperSerializer
    queryset = Price.objects.all()
    permission_classes = (IsAdminUser,)


class FilmViewSet(ViewSetInsert, viewsets.ModelViewSet):
    queryset = Film.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.FilmHyperSerializer
        else:
            return serial.FilmCUDSerializer


class HallViewSet(ViewSetInsert, viewsets.ModelViewSet):
    serializer_class = serial.HallHyperSerializer
    queryset = Hall.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.HallHyperSerializer
        else:
            return serial.HallCUDSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.base_seances.count():
            return Response(f'There are related to this hall '
                            f'SeanceBase objects. Can\'t delete', status=status.HTTP_200_OK)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateSeatsAPIView(CreateAPIView):
    permission_classes = (IsAdminUser, )

    def post(self, request, *args, **kwargs):
        serializer = serial.CreateSeatsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# class ImageUploadAPIView(UpdateAPIView):
#     permission_classes = (IsAdminUser, )
#     parser_classes = (FileUploadParser, )
#     queryset = Film.objects.all()
#
#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         image_serializer = serial.ImageSerializer(data=request.data)
#
#         if image_serializer.is_valid():
#             instance.image = image_serializer.data
#             # image_serializer.save()
#             return Response(image_serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
