from django import forms
from datetime import datetime, timedelta

import calendar

periods = []
today = datetime.today()
for p in range(5):
    if today.weekday() + p - today.weekday() == 0:
        periods.append( ('Today', 'Today') )
    elif today.weekday() + p - today.weekday() == 1:
        periods.append( ('Tomorrow', 'Tomorrow') )
    else:
        periods.append(
            (calendar.day_name[(today + timedelta(days=p)).weekday()], calendar.day_name[(today + timedelta(days=p)).weekday()] )
        )



class WeatherDataForm(forms.Form):
    city = forms.CharField(max_length=30)
    period= forms.CharField(label='Select period?', widget=forms.Select(choices=periods))

    def clean(self):
        cleaned_data = super(WeatherDataForm, self).clean()
        city = cleaned_data.get('city')
        period = cleaned_data.get('period')
        if not city and not period:
            raise forms.ValidationError('Please fill in the form!')