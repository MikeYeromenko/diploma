from django.shortcuts import get_object_or_404
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
        hall = get_object_or_404(Hall, pk=kwargs.get('pk'))
        seat_category = get_object_or_404(SeatCategory, pk=serializer['seat_category'].value)
        hall.create_or_update_seats(seat_category=seat_category,
                                    row=serializer['row'].value,
                                    number_starts=serializer['seat_starts'].value,
                                    number_ends=serializer['seat_ends'].value)
        result = hall.activate_hall()
        if result['success']:
            return Response({
                'created_seats': serial.SeatModelSerializer(hall.seats.all(), many=True).data,
                'detail': f'Hall is successfully activated'
            }, status=status.HTTP_200_OK)
            # return Response(serial.SeatsCreatedSerializer({
            #     'created_seats': hall.seats.all(),
            #     'detail': f'Hall is successfully activated'
            # }).data, status=status.HTTP_200_OK)
        # return Response({
        #         'created_seats': serial.SeatModelSerializer(hall.seats.all(), many=True),
        #         'detail': f'There leaved {result["uncreated_seats"]} uncreated seats'
        #     }, status=status.HTTP_200_OK)
        return Response(serial.SeatsCreatedSerializer({
            'created_seats': hall.seats.all(),
            'detail': f'There leaved {result["uncreated_seats"]} uncreated seats'
        }).data, status=status.HTTP_201_CREATED)


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
