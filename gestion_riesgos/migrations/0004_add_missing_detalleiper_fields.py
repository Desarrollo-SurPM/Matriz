# Generated manually to fix missing fields in DetalleIPER

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_riesgos', '0003_matriziper_detalleiper'),
    ]

    operations = [
        # Add the missing simple evaluation fields
        migrations.AddField(
            model_name='detalleiper',
            name='eval_probabilidad',
            field=models.IntegerField(verbose_name='P', blank=True, null=True, default=0),
        ),
        migrations.AddField(
            model_name='detalleiper',
            name='eval_severidad',
            field=models.IntegerField(verbose_name='S', blank=True, null=True, default=0),
        ),
        migrations.AddField(
            model_name='detalleiper',
            name='eval_valor',
            field=models.IntegerField(verbose_name='Valor Riesgo', blank=True, null=True, default=0),
        ),
        migrations.AddField(
            model_name='detalleiper',
            name='eval_clasificacion',
            field=models.CharField(max_length=50, verbose_name='Clasificación', blank=True, null=True),
        ),
    ]
