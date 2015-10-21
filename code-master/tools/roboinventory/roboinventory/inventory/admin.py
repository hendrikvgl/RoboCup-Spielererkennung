from django.contrib import admin

from roboinventory.inventory.models import Roboter, Hardware, HardwareLog, \
        AttachedHardware, format_datetime

class RoboterInline(admin.TabularInline):
    model = AttachedHardware
    ordering = ('position', )

class RoboterAdmin(admin.ModelAdmin):
    inlines = [RoboterInline]

class HardwareAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'status')
    list_editable = ('status', )
    list_filter = ('status', 'type')

class HardwareLogAdmin(admin.ModelAdmin):
    list_display = ('change_date', 'hardware', 'status', 'note')
    search_field = ('hardware__id', )

def start_date(obj):
    return format_datetime(obj.start_date)
start_date.short_description = 'Attached'

def end_date(obj):
    if not obj.end_date:
        return u'Not detached yet'
    return format_datetime(obj.end_date)
end_date.short_description = 'Detached'

class AttachedHardwareAdmin(admin.ModelAdmin):
    list_display = ('roboter', 'hardware', 'position', start_date, end_date)
    list_filter = ('roboter', )
    search_fields = ('hardware__id', )

admin.site.register(Roboter, RoboterAdmin)
admin.site.register(Hardware, HardwareAdmin)
admin.site.register(HardwareLog, HardwareLogAdmin)
admin.site.register(AttachedHardware, AttachedHardwareAdmin)
