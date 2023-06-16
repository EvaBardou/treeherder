# Generated by Django 3.0.3 on 2020-03-02 10:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('perf', '0025_provide_tag_support'),
    ]

    operations = [
        migrations.AddField(
            model_name='backfillrecord',
            name='log_details',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='backfillrecord',
            name='status',
            field=models.IntegerField(
                choices=[
                    (0, 'Preliminary'),
                    (1, 'Ready for processing'),
                    (2, 'Backfilled'),
                    (3, 'Finished'),
                    (4, 'Failed'),
                ],
                default=0,
            ),
        ),
    ]
