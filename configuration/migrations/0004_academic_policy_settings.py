from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0003_admin_and_cli_file_handling_noop'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicPolicySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repeat_policy', models.CharField(
                    max_length=16,
                    choices=[
                        ('ALL', 'Count all attempts'),
                        ('LATEST', 'Use latest attempt per course'),
                        ('BEST', 'Use best attempt per course'),
                    ],
                    default='ALL',
                )),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
