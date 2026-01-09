from django.db import migrations, models


def forwards_copy_core_settings(apps, schema_editor):
    """Copy data from legacy core.CollegeSettings into configuration.CollegeSettings."""
    CoreCollegeSettings = apps.get_model('core', 'CollegeSettings')
    ConfigCollegeSettings = apps.get_model('configuration', 'CollegeSettings')

    legacy = CoreCollegeSettings.objects.order_by('id').first()
    if not legacy:
        return

    # Ensure singleton row exists in configuration
    cfg, _created = ConfigCollegeSettings.objects.get_or_create(pk=1)

    # Copy overlapping/meaningful fields
    if getattr(cfg, 'college_name', None) in (None, ''):
        cfg.college_name = legacy.college_name

    # Map legacy assets
    # - legacy.logo -> cfg.college_logo (same upload_to)
    # - legacy.signature -> cfg.signature (new field added for compatibility)
    if not cfg.college_logo and getattr(legacy, 'logo', None):
        cfg.college_logo = legacy.logo

    if not getattr(cfg, 'signature', None) and getattr(legacy, 'signature', None):
        cfg.signature = legacy.signature

    # Map legacy letterhead
    if getattr(cfg, 'letterhead', None) in (None, '') and getattr(legacy, 'letterhead', None):
        cfg.letterhead = legacy.letterhead

    cfg.save()


class Migration(migrations.Migration):
    dependencies = [
        ('configuration', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collegesettings',
            name='signature',
            field=models.ImageField(blank=True, null=True, upload_to='college_signatures/'),
        ),
        migrations.AddField(
            model_name='collegesettings',
            name='letterhead',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(forwards_copy_core_settings, migrations.RunPython.noop),
    ]
