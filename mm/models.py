from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html
from django import forms


class InvoiceTitle(models.Model):
    title = models.CharField("发票抬头", max_length=100)
    tariffItem = models.CharField("税号", max_length=50, unique=True)

    class Meta:
        verbose_name = '发票抬头'
        verbose_name_plural = '发票抬头'

    def __str__(self):
        return '%s-%s' % (self.title, self.tariffItem)


class Contract(models.Model):
    Management_to_the_rest = (
        (1, '由公司暂时保管（历史合同）'),
        (2, '需返样'),
        (3, "项目结题3个月后，公司自行处理")
    )
    RANGE_CHOICES = (
        (2, '总监底价'),
        (1, '高于销售底价'),
        (3, '低于总监底价'),
    )
    TYPE_CHOICES = (
        (1, '16S/ITS'),
        (2, '宏基因组'),
        (3, '单菌'),
        (4, '转录组'),
        (5, '其它'),
        (6, '无'),
        (7, '代谢组'),
    )
    CONTRACT_TYPE = (
        (1, '流程合同'),
        (2, '预付款合同'),
    )
    # 选项
    STATUS_CHOICES = (
        (1, '新合同'),  #创建新合同默认的状态
        (2, '已申请开票'),  #提交第一个发票申请的状态
        (3, '已完成'),  #合同的总款额的发票都已经开出的状态
    )
    contract_number = models.CharField('合同号', max_length=30, unique=True)
    name = models.CharField('合同名', max_length=100)
    type = models.IntegerField(
        '类型',
        choices=TYPE_CHOICES
    )
    salesman = models.ForeignKey(User, verbose_name='业务员', on_delete=models.SET_NULL, null=True)
    price = models.DecimalField('单价', max_digits=7, decimal_places=2, null=True)
    price_range = models.IntegerField(
        '价格区间',
        choices=RANGE_CHOICES, blank=True,null=True
    )
    all_amount = models.DecimalField('总款额', max_digits=12, decimal_places=2)
    fis_amount = models.DecimalField('首款额', max_digits=12, decimal_places=2)
    fis_date = models.DateField('首款到款日', blank=True, null=True)
    fis_amount_in = models.DecimalField('已到首款额', max_digits=12, null=True,decimal_places=2, default=0)
    fin_amount = models.DecimalField('尾款额', max_digits=12, decimal_places=2, default=0)
    fin_date = models.DateField('尾款到款日', blank=True, null=True)
    fin_amount_in = models.DecimalField('已到尾款额', max_digits=12,null=True, decimal_places=2, default=0)
    send_date = models.DateField('合同寄出日', null=True, blank=True)
    tracking_number = models.CharField('快递单号', max_length=15, blank=True)
    receive_date = models.DateField('合同寄回日', null=True, blank=True)
    contract_file = models.FileField('附件', upload_to='uploads/%Y/%m',blank=True)
    contract_file_scanning = models.FileField('扫描件', upload_to='uploads/contractScanning/%Y/%m', blank=True, null=True)
    contacts = models.CharField('合同联系人', max_length=15, default="",null=True)
    contacts_email = models.EmailField(verbose_name="合同联系人邮箱", default='',null=True)
    contact_phone = models.CharField('合同联系人电话', max_length=30, blank=True,null=True,default="")
    contact_address = models.CharField('合同联系人地址', max_length=30, blank=True,null=True)
    partner_company = models.CharField(max_length=200, verbose_name="合作伙伴单位", default="",null=True)
    use_amount = models.DecimalField("已使用的金额", null=True, blank=True, max_digits=12, decimal_places=2, default=0)
    contact_note = models.TextField('合同备注', blank=True,null=True,default="")
    is_status = models.IntegerField('状态', choices=STATUS_CHOICES, default=1) #1初始状态，2首款到齐，3尾款到齐
    management_to_rest = models.IntegerField(choices=Management_to_the_rest,
                                             verbose_name="剩余样品处理方式",
                                             default=1)

    consume_money = models.DecimalField('预存款合同已消耗金额', max_digits=12, decimal_places=2, default=0)
    contract_type = models.IntegerField('合同类型', choices=CONTRACT_TYPE, default=1)

    class Meta:
        verbose_name = '合同管理'
        verbose_name_plural = '合同管理'

    def file_link(self):
        if self.contract_file:
            return format_html("<a href='%s'>下载</a>" % (self.contract_file.url))
        else:
            return "未上传"
    file_link.short_description = "附件"
    file_link.allow_tags = True

    def file_link_scanning(self):
        if self.contract_file_scanning:
            return format_html("<a href='%s'>下载</a>" % (self.contract_file_scanning.url))
        else:
            return "未上传"
    file_link_scanning.short_description = "附件"
    file_link_scanning.allow_tags = True

    def __str__(self):
        return '【%s】-【%s】' % (self.contract_number, self.name)

class Contract_execute(models.Model):
    contract = models.ManyToManyField(Contract, verbose_name="对应预存款合同")
    all_amount = models.DecimalField('总款额', max_digits=12, decimal_places=2)
    contract_number = models.CharField('执行合同号', max_length=30, unique=True)
    contact_note = models.TextField('执行合同备注', blank=True)
    saler = models.ForeignKey(User,
                              verbose_name='业务员', on_delete=models.SET_NULL, null=True)
    submit = models.BooleanField("提交",default=False)
    contract_file = models.FileField('附件',
                                     upload_to='uploads/Contract_execute/%Y/%m',
                                     blank=True)
    def __str__(self):
        return self.contract_number

    class Meta:
        verbose_name = '执行合同管理'
        verbose_name_plural = '执行合同管理'


class Invoice(models.Model):
    PERIOD_CHOICES = (
        ('FIS', '首款'),
        ('FIN', '尾款'),
    )
    INVOICE_TYPE_CHOICES = (
        ('CC', '普票'),
        ('SC', '专票'),
    )
    ISSUING_UNIT_CHOICES = (
        ('sh', '上海锐翌'),
        ('hz', '杭州拓宏'),
        ('sd', '山东锐翌'),
        ('sz', '金锐生物'),
        ('qd', '青岛锐翌'),
    )
    contract = models.ForeignKey(
        Contract,
        verbose_name='合同',
        on_delete=models.CASCADE,
    )
    title = models.ForeignKey(InvoiceTitle, verbose_name='发票抬头', on_delete=models.SET_NULL, null=True)
    issuingUnit = models.CharField('开票单位', choices=ISSUING_UNIT_CHOICES, max_length=25, default='sh',null=True)
    period = models.CharField('款期', max_length=3, choices=PERIOD_CHOICES, default='FIS')
    amount = models.DecimalField('发票金额', max_digits=9, decimal_places=2)
    type = models.CharField('发票类型', max_length=3, choices=INVOICE_TYPE_CHOICES, default='CC')
    content = models.CharField('发票内容', max_length=200, null=True)
    note = models.TextField('备注', null=True)
    submit = models.BooleanField('提交开票',default=False)

    class Meta:
        verbose_name = '开票申请'
        verbose_name_plural = '开票申请'

    def __str__(self):
        return '%.2f' % self.amount


class BzContract(models.Model):
    contract = models.ManyToManyField(Contract, verbose_name="对应合同", blank=True)

    contract_number = models.CharField('报账合同号', max_length=30, unique=True)
    name = models.CharField('报账合同名', max_length=100)
    salesman = models.ForeignKey(User, verbose_name='业务员', on_delete=models.SET_NULL, null=True)
    contact_note = models.TextField('报账合同备注', blank=True)

    send_date = models.DateField('合同寄出日', null=True, blank=True)
    tracking_number = models.CharField('快递单号', max_length=15, blank=True)
    receive_date = models.DateField('合同寄回日', null=True, blank=True)
    contract_file = models.FileField('附件', upload_to='uploads/BzContract/%Y/%m', blank=True)


    def file_link(self):
        if self.contract_file:
            return format_html("<a href='%s'>下载</a>" % (self.contract_file.url))
        else:
            return "未上传"
    file_link.short_description = "附件"
    file_link.allow_tags = True

    class Meta:
        verbose_name = '报账合同管理'
        verbose_name_plural = '报账合同管理'

    def __str__(self):
        return '【%s】-【%s】' % (self.contract_number, self.name)