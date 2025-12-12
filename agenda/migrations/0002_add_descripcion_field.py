# Generated manually to fix missing column

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='visita',
            name='descripcion',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
