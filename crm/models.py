from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

from docx_parsing_gmdzy2010.utilities import Price2UpperChinese
# from datetime import date


class Customer(models.Model):
    """客户管理模型"""
    # TODO: 表名称更改为Clients更合理
    LEVEL_CHOICES = (
        (1, '一般'),
        (2, '重要'),
        (3, '非常重要'),
    )
    linker = models.ForeignKey(
        User, verbose_name='联络人', on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(
        verbose_name='客户姓名', max_length=12
    )
    organization = models.CharField(
        verbose_name='单位（全称）', max_length=20
    )
    department = models.CharField(
        verbose_name='院系/科室（全称）', max_length=20, default=''
    )
    address = models.CharField(
        verbose_name='办公地址', max_length=50
    )
    title = models.CharField(
        verbose_name='职务', max_length=50, default=''
    )
    # 提示需要添加默认值
    contact = models.PositiveIntegerField(
        verbose_name='联系方式', default=0
    )
    email = models.EmailField(
        verbose_name='邮箱'
    )
    level = models.IntegerField(
        verbose_name='客户分级', choices=LEVEL_CHOICES, default=1
    )
    
    class Meta:
        verbose_name = "客户管理"
        verbose_name_plural = "客户管理"

    def __str__(self):
        return "%s" % self.name


class Intention(models.Model):
    """意向管理模型"""
    TYPE_CHOICES = (
        (1, '16S/ITS'),
        (2, '宏基因组'),
        (3, '单菌'),
        (4, '转录组'),
        (5, '其它'),
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name='客户',
    )
    project_name = models.CharField(
        verbose_name='项目名称', max_length=50
    )
    project_type = models.IntegerField(
        verbose_name='项目类型', choices=TYPE_CHOICES, default=1
    )
    amount = models.IntegerField(
        verbose_name='数量'
    )
    closing_date = models.DateField(
        verbose_name='预计成交时间', auto_now_add=True
    )
    price = models.DecimalField(
        verbose_name='预计成交价', max_digits=12, decimal_places=2
    )

    class Meta:
        verbose_name = "意向管理"
        verbose_name_plural = "意向管理"

    def __str__(self):
        return "%s" % self.project_name


class IntentionRecord(models.Model):
    intention = models.ForeignKey(
        Intention, verbose_name='意向项目', on_delete=models.SET_NULL, null=True
    )
    status = models.CharField(
        verbose_name='进展/状态', max_length=15
    )
    record_date = models.DateField(
        verbose_name='跟进时间', auto_now_add=True
    )
    note = models.TextField(
        verbose_name='备注', blank=True
    )

    class Meta:
        verbose_name = '进展记录'
        verbose_name_plural = '进展记录'

    def __str__(self):
        return '%s-%s' % (self.status, self.record_date)


class Analyses(models.Model):
    """分析条目管理"""
    ANALYSIS_TYPE_CHOICES = (
        (1, '16S--标准分析'),
        (2, '16S--高级分析'),
        (3, '16S--个性化分析'),
        (4, 'META--标准分析'),
        (5, 'META--高级分析'),
        (6, 'META--个性化分析'),
    )
    union_id = models.CharField(
        verbose_name="分析统一编号", max_length=32, primary_key=True
    )
    analysis_name = models.CharField(
        verbose_name="分析名称", max_length=128,
    )
    analysis_type = models.IntegerField(
        verbose_name="分析所属类别", choices=ANALYSIS_TYPE_CHOICES
    )
    
    class Meta:
        verbose_name = '分析条目'
        verbose_name_plural = '分析条目'

    def __str__(self):
        return '{}（{}）'.format(
            self.analysis_name, self.union_id
        )


class ContractApplications(models.Model):
    """销售合同申请"""
    PROJECT_TYPE_CHOICES = (
        (1, '16S/ITS'),
        (2, '宏基因组'),
        (3, '单菌'),
        (4, '转录组'),
        (5, '代谢组'),
        (6, '其它'),
    )
    PAY_TYPE_CHOICES = (
        (1, '全款'),
        (2, '首尾款'),
    )
    SECOND_PARTY_CHOICES = (
        (1, '上海锐翌生物科技有限公司'),
        (2, '杭州锐翌基因技术有限公司'),
        (3, '山东锐翌基因技术有限公司'),
        (4, '杭州拓宏生物科技有限公司'),
        (5, '深圳金锐生物科技有限公司'),
    )
    DATA_DELIVERY_CHOICES = (
        (1, '项目数据小于50G，甲方选择使用百度网盘进行数据交付，费用￥0.00（零圆整）'),
        (2, '项目数据小于16G，甲方选择使用U盘进行数据交付，费用￥70.00（柒拾圆整）'),
        (3, '项目数据小于32G，甲方选择使用U盘进行数据交付，费用￥150.00（壹佰伍拾圆整）'),
        (4, '项目数据小于500G，甲方选择使用移动硬盘进行数据交付，费用￥500.00（伍佰圆整）'),
        (5, '项目数据小于1T，甲方选择使用移动硬盘进行数据交付，费用￥700.00（柒佰圆整）'),
    )
    contract_name = models.CharField(
        verbose_name="合同名称", max_length=512,
        help_text="单位缩写+数量+样本类型+项目+测序分析"
    )
    project_type = models.SmallIntegerField(
        verbose_name='项目类型', choices=PROJECT_TYPE_CHOICES, default=1,
    )
    pay_type = models.SmallIntegerField(
        verbose_name="付款方式", choices=PAY_TYPE_CHOICES, default=1
    )
    
    # 甲方信息字段
    first_party = models.CharField(
        verbose_name="委托方（甲方）", max_length=256, null=True, blank=True,
    )
    first_party_contact = models.CharField(
        verbose_name="甲方联系人", max_length=256, null=True, blank=True,
    )
    first_party_contact_phone = models.CharField(
        verbose_name="甲方联系人电话", max_length=32, null=True, blank=True,
    )
    first_party_contact_email = models.EmailField(
        verbose_name="甲方邮箱", max_length=32, null=True, blank=True,
    )
    first_party_address = models.CharField(
        verbose_name="甲方通讯地址", max_length=256, null=True, blank=True,
    )
    
    # 乙方信息字段
    second_party = models.SmallIntegerField(
        verbose_name="受托方（乙方）", default=1, choices=SECOND_PARTY_CHOICES,
    )
    second_party_contact = models.ForeignKey(
        User, verbose_name="乙方联系人", on_delete=models.SET_NULL, null=True,
    )
    second_party_contact_phone = models.CharField(
        verbose_name="乙方联系人电话", max_length=32, null=True, blank=True,
    )
    second_party_contact_email = models.EmailField(
        verbose_name="乙方联系人邮箱", max_length=32, null=True, blank=True,
    )
    second_party_company_email = models.EmailField(
        verbose_name="乙方邮箱", max_length=32, default="support@realbio.cn"
    )
    second_party_address = models.CharField(
        verbose_name="乙方通讯地址", max_length=256, null=True, blank=True,
        default="上海市闵行区浦江高科技园区新骏环路138号6幢302室",
    )
    signed_date = models.DateField(
        verbose_name="签订日期", default=now
    )
    valid_date = models.DateField(
        verbose_name="有效日期至", default=now
    )
    platform = models.CharField(
        verbose_name="测序平台", max_length=256, default="Illumina PE250",
    )
    reads_minimum = models.SmallIntegerField(
        verbose_name="序列读长下限(万条)", default=3
    )
    start_delay_sample_counts = models.SmallIntegerField(
        verbose_name="延迟启动样品数量", null=True, blank=True, default=100
    )
    extract_sample_counts = models.SmallIntegerField(
        verbose_name="提取样本数量", null=True, blank=True, default=100
    )
    sequence_sample_counts = models.SmallIntegerField(
        verbose_name="测序样本数量", null=True, blank=True, default=100
    )
    databasing_upper_limit = models.SmallIntegerField(
        verbose_name="建库天数上限", null=True, blank=True, default=7,
    )
    delivery_upper_limit = models.SmallIntegerField(
        verbose_name="交付天数上限", default=45
    )
    data_delivery_type = models.SmallIntegerField(
        verbose_name="数据交付形式", default=1, choices=DATA_DELIVERY_CHOICES,
    )
    
    # 价格信息
    total_price = models.DecimalField(
        verbose_name="项目总价", max_digits=16, decimal_places=2
    )
    sequence_single_price = models.DecimalField(
        verbose_name="测序分析单价", max_digits=16, decimal_places=2,
        default=300,
    )
    sequence_total_price = models.DecimalField(
        verbose_name="测序分析总价", max_digits=16, decimal_places=2
    )
    extract_total_price = models.DecimalField(
        verbose_name="提取总价", max_digits=16, decimal_places=2,
    )
    sample_return_price = models.DecimalField(
        verbose_name="返样总价", max_digits=16, decimal_places=2,
        default=500,
    )
    data_delivery_price = models.DecimalField(
        verbose_name="数据交付总价", max_digits=16, decimal_places=2,
        default=500,
    )
    first_payment =  models.DecimalField(
        verbose_name="首款", max_digits=16, decimal_places=2,
        null=True, blank=True,
    )
    final_payment = models.DecimalField(
        verbose_name="尾款", max_digits=16, decimal_places=2,
        null=True, blank=True,
    )
    analyses_aa = models.ManyToManyField(
        Analyses, verbose_name="高级分析", blank=True,
        limit_choices_to={"union_id__contains": "AA"},
        related_name="analyses_aa"
    )
    analyses_pa = models.ManyToManyField(
        Analyses, verbose_name="个性化分析", blank=True,
        limit_choices_to={"union_id__contains": "PA"},
        related_name="analyses_pa"
    )
    contract_file = models.FileField(
        verbose_name="合同", null=True, blank=True,
        upload_to="uploads/contract/%Y/%m/%d/"
    )
    
    @property
    def total_price_upper(self):
        return Price2UpperChinese(self.total_price)
    
    @property
    def sequence_single_price_upper(self):
        return Price2UpperChinese(self.sequence_single_price)
    
    @property
    def sequence_total_price_upper(self):
        return Price2UpperChinese(self.sequence_total_price)
    
    @property
    def extract_total_price_upper(self):
        return Price2UpperChinese(self.extract_total_price)
    
    @property
    def sample_return_price_upper(self):
        return Price2UpperChinese(self.sample_return_price)
    
    @property
    def data_delivery_price_upper(self):
        return Price2UpperChinese(self.data_delivery_price)
    
    @property
    def first_payment_upper(self):
        return Price2UpperChinese(self.first_payment)
    
    @property
    def final_payment_upper(self):
        return Price2UpperChinese(self.final_payment)
        
    class Meta:
        verbose_name = '合同申请'
        verbose_name_plural = '合同申请'
    
    def __str__(self):
        return '%s' % self.contract_name
