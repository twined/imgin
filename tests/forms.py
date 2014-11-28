from imgin.forms import BaseImageSeriesForm
from .models import PfSeries


class PfSeriesForm(BaseImageSeriesForm):
    class Meta:
        model = PfSeries
        exclude = ('user', 'order',)
