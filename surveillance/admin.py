from django.contrib import admin
from .models import Information


class InformationAdmin(admin.ModelAdmin):

    list_display    = [ "id","url","email","user_id" ]
    #list_editable   = [ "url","email" ]

    
    search_fields   = [ "id","url","email" ]

    list_per_page       = 20000
    list_max_show_all   = 20000


admin.site.register(Information,InformationAdmin)
#admin.site.register(Information)
