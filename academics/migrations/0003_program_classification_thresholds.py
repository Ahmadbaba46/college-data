from django.db import migrations, models
import django.db.models.deletion


def seed_default_thresholds(apps, schema_editor):
    Program = apps.get_model('academics', 'Program')
    Threshold = apps.get_model('academics', 'ProgramClassificationThreshold')

    for p in Program.objects.all():
        if Threshold.objects.filter(program=p).exists():
            continue

        if p.classification_scheme == 'BSC':
            defaults = [
                ('First Class', 3.5),
                ('Second Class Upper', 3.0),
                ('Second Class Lower', 2.0),
                ('Third Class', 1.0),
                ('Fail', 0.0),
            ]
        else:
            defaults = [
                ('Distinction', 3.5),
                ('Upper Credit', 3.0),
                ('Lower Credit', 2.5),
                ('Pass', 2.0),
                ('Fail', 0.0),
            ]

        for label, min_cgpa in defaults:
            Threshold.objects.create(program=p, label=label, min_cgpa=min_cgpa)


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0002_program_min_units'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramClassificationThreshold',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=64)),
                ('min_cgpa', models.FloatField()),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classification_thresholds', to='academics.program')),
            ],
            options={
                'unique_together': {('program', 'label')},
                'ordering': ['-min_cgpa'],
            },
        ),
        migrations.RunPython(seed_default_thresholds, migrations.RunPython.noop),
    ]
