from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
        ('configuration', '0002_unify_college_settings'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CollegeSettings',
        ),
    ]
