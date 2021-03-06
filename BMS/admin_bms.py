# -*- coding: UTF-8 -*-
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import User, UserAdmin, Group, GroupAdmin
from djcelery.admin import IntervalSchedule, CrontabSchedule, PeriodicTaskAdmin, PeriodicTask, TaskState, TaskMonitor, \
    WorkerMonitor, WorkerState
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy
from django.views.decorators.cache import never_cache
from urllib import parse
from BMS.settings import DINGTALK_APPID


class BMSAdminSite(AdminSite):
    site_title = "BMS网站管理"
    site_header = ugettext_lazy('后台管理')
    login_template = "admin/login.html"

    @never_cache
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = self.get_app_list(request)
        context = dict(
            self.each_context(request),
            title=self.index_title,
            app_list=app_list,
        )
        context.update(extra_context or {})
        request.current_app = self.name
        return TemplateResponse(
            request, self.index_template or 'admin/index.html', context
        )

    def each_context(self, request):
        """
        Returns a dictionary of variables to put in the template context for
        *every* page in the admin site.

        For sites running on a subpath, use the SCRIPT_NAME value if site_url
        hasn't been customized.
        """
        script_name = request.META['SCRIPT_NAME']
        site_url = script_name if self.site_url == '/' and script_name else self.site_url
        # 把用户的groupID传给template
        # if Group.objects.filter(id = request.user.id):
        #     group_context = Group.objects.get(id = request.user.id).id
        # else:
        #     group_context = 0
        # group_context = [0, ]
        # if not isinstance(request.user,AnonymousUser):
        try:
            groups = Group.objects.filter(user=request.user)
            if groups:
                group_context = [i.name for i in groups]
            else:
                if request.user.is_superuser:
                    group_context = [1, ]
                else:
                    # 此类用户没有分组
                    group_context = [0, ]
        except:
            group_context = [0, ]

        return {
            'site_title': self.site_title,
            'site_header': self.site_header,
            'site_url': site_url,
            'has_permission': self.has_permission(request),
            'group_id': group_context,
            'available_apps': self.get_app_list(request),
        }

    @never_cache
    def login(self, request, extra_context=None):
        extra_context = extra_context or {}
        url = "http://{}/dingtalk_auth/".format(request.META["HTTP_HOST"])
        redirect_uri = parse.quote(url)
        params = {
            "appid": DINGTALK_APPID,
            "response_type": "code",
            "scope": "snsapi_login",
            "state": "test",
            "redirect_uri": redirect_uri,
        }
        uri_main = "https://oapi.dingtalk.com/connect/qrconnect"
        uri_params = "?appid={appid}&response_type={response_type}&" \
                     "scope={scope}&state={state}&" \
                     "redirect_uri={redirect_uri}".format(**params)
        dingtalk_qrcode_uri = "{}{}".format(uri_main, uri_params)
        extra_context["dingtalk_qrcode_uri"] = dingtalk_qrcode_uri
        return super().login(request, extra_context=extra_context)


BMS_admin_site = BMSAdminSite()
BMS_admin_site.register(User, UserAdmin)
BMS_admin_site.register(Group, GroupAdmin)
BMS_admin_site.register(IntervalSchedule)
BMS_admin_site.register(CrontabSchedule)
BMS_admin_site.register(PeriodicTask, PeriodicTaskAdmin)
BMS_admin_site.register(TaskState, TaskMonitor)
BMS_admin_site.register(WorkerState, WorkerMonitor)
