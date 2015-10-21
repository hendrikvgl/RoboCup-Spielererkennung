from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.utils.dateformat import format as date_format

ROBOTER_POSITIONS = (
    ('engine1', 'Engine 1 (RShoulderPitch)'),
    ('engine2', 'Engine 2 (LShoulderPitch)'),
    ('engine3', 'Engine 3 (RShoulderRoll)'),
    ('engine4', 'Engine 4 (LShoudlerRoll)'),
    ('engine5', 'Engine 5 (RElbow)'),
    ('engine6', 'Engine 6 (LElbow)'),
    ('engine7', 'Engine 7 (RHipYaw)'),
    ('engine8', 'Engine 8 (LHipYaw)'),
    ('engine9', 'Engine 9 (RHipRoll)'),
    ('engine10', 'Engine 10 (LHipRoll)'),
    ('engine11', 'Engine 11 (RHipPitch)'),
    ('engine12', 'Engine 12 (LHipPitch)'),
    ('engine13', 'Engine 13 (RKnee)'),
    ('engine14', 'Engine 14 (LKnee)'),
    ('engine15', 'Engine 15 (RAnklePitch)'),
    ('engine16', 'Engine 16 (LAnklePitch)'),
    ('engine17', 'Engine 17 (RAnkleRoll)'),
    ('engine18', 'Engine 18 (LAnkleRoll)'),
    ('engine19', 'Engine 19 (HeadPan)'),
    ('engine20', 'Engine 20 (HeadTilt)'),
)

HARDWARE_TYPES = (
    ('engine', 'Engine'),
    ('battery', 'Battery'),
    ('charger', 'Charger'),
    ('smallpart','Small Part'),
)

HARDWARE_STATUSES = (
    ('ok', 'OK'),
    ('broken', 'Broken'),
    ('missing', 'Missing'),
)

def format_datetime(d):
    return date_format(d, 'Y-d-m H:i')

class Hardware(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    type = models.CharField(max_length=20, choices=HARDWARE_TYPES)
    status = models.CharField(max_length=20, choices=HARDWARE_STATUSES)
    note = models.TextField(blank=True)

    def __unicode__(self):
        return self.pk

class HardwareLog(models.Model):
    hardware = models.ForeignKey(Hardware)
    change_date = models.DateTimeField(default=datetime.today)
    status = models.CharField(max_length=20, choices=HARDWARE_STATUSES)
    note = models.TextField(blank=True)

    def __unicode__(self):
        return u'[{0}] {1}'.format(date_format(self.change_date, 
            'SHORT_DATETIME_FORMAT'), unicode(self.hardware))

    class Meta:
        ordering = ('-change_date', )

class Roboter(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.pk)

class AttachedHardware(models.Model):
    hardware = models.ForeignKey(Hardware)
    roboter = models.ForeignKey(Roboter)
    position = models.CharField(max_length=20, choices=ROBOTER_POSITIONS)
    start_date = models.DateTimeField(default=datetime.today)
    end_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        if self.end_date:
            return u'From {0} to {1}: {2} in {3}'.format(
                    format_datetime(self.start_date),
                    format_datetime(self.end_date),
                    unicode(self.hardware), unicode(self.roboter))
        else:
            return u'{0} in {1} (since {2})'.format(unicode(self.hardware),
                    unicode(self.roboter), format_datetime(self.start_date))

    class Meta:
        ordering = ('roboter', '-end_date')

def attached_hardware_cb(sender, instance, created, **kwargs):
    if created:
        attached_hw =AttachedHardware.objects.exclude(roboter=instance.roboter,
                position=instance.position).__filter(hardware=instance.hardware,
                end_date=None)
        for hw in attached_hw:
            hw.end_date = instance.start_date
            hw.save()

def changed_hardware_cb(sender, instance, created, **kwargs):
    HardwareLog.objects.create(hardware=instance, status=instance.status,
            note=instance.note)

post_save.connect(attached_hardware_cb, sender=AttachedHardware)
post_save.connect(changed_hardware_cb, sender=Hardware)
