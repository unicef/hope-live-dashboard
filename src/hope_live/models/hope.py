from django.db import models


class HopeModel(models.Model):
    class Meta:
        abstract = True
        managed = False


class BusinessArea(HopeModel):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=250, unique=True)
    active = models.BooleanField(null=True)
    region_name = models.CharField(max_length=8, blank=True)

    class Meta:
        db_table = "core_businessarea"

    def __str__(self) -> str:
        return self.name


class HopeProgram(HopeModel):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    is_visible = models.BooleanField(default=True, null=True)
    is_removed = models.BooleanField(default=False, null=True)
    business_area = models.ForeignKey(BusinessArea, on_delete=models.DO_NOTHING, db_column="business_area_id")

    class Meta:
        db_table = "program_program"

    def __str__(self) -> str:
        return self.name


class DeliveryMechanism(HopeModel):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "payment_deliverymechanism"

    def __str__(self) -> str:
        return self.name


class FinancialServiceProvider(HopeModel):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "payment_financialserviceprovider"

    def __str__(self) -> str:
        return self.name


class Area(HopeModel):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "geo_area"

    def __str__(self) -> str:
        return self.name


class Household(HopeModel):
    id = models.UUIDField(primary_key=True)
    business_area = models.ForeignKey(BusinessArea, on_delete=models.DO_NOTHING, db_column="business_area_id")
    admin1 = models.ForeignKey(Area, on_delete=models.DO_NOTHING, db_column="admin1_id", blank=True, null=True)
    is_removed = models.BooleanField(default=False)
    size = models.IntegerField(default=1)

    children_count = models.IntegerField(null=True, blank=True)
    female_age_group_0_5_disabled_count = models.IntegerField(default=0, null=True)
    female_age_group_6_11_disabled_count = models.IntegerField(default=0, null=True)
    female_age_group_12_17_disabled_count = models.IntegerField(default=0, null=True)
    female_age_group_18_59_disabled_count = models.IntegerField(default=0, null=True)
    female_age_group_60_disabled_count = models.IntegerField(default=0, null=True)
    male_age_group_0_5_disabled_count = models.IntegerField(default=0, null=True)
    male_age_group_6_11_disabled_count = models.IntegerField(default=0, null=True)
    male_age_group_12_17_disabled_count = models.IntegerField(default=0, null=True)
    male_age_group_18_59_disabled_count = models.IntegerField(default=0, null=True)
    male_age_group_60_disabled_count = models.IntegerField(default=0, null=True)

    class Meta:
        db_table = "household_household"

    def __str__(self) -> str:
        return f"Household {self.id}"

    @property
    def pwd_count(self) -> int:
        fields = [
            self.female_age_group_0_5_disabled_count,
            self.female_age_group_6_11_disabled_count,
            self.female_age_group_12_17_disabled_count,
            self.female_age_group_18_59_disabled_count,
            self.female_age_group_60_disabled_count,
            self.male_age_group_0_5_disabled_count,
            self.male_age_group_6_11_disabled_count,
            self.male_age_group_12_17_disabled_count,
            self.male_age_group_18_59_disabled_count,
            self.male_age_group_60_disabled_count,
        ]
        return sum(f or 0 for f in fields)


class PaymentPlan(HopeModel):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    business_area = models.ForeignKey(BusinessArea, on_delete=models.DO_NOTHING, db_column="business_area_id")
    status = models.CharField(max_length=50)

    class Meta:
        db_table = "payment_paymentplan"

    def __str__(self) -> str:
        return self.name or str(self.id)


class Payment(HopeModel):
    id = models.UUIDField(primary_key=True)
    status = models.CharField(max_length=255)
    currency = models.CharField(max_length=4, blank=True)
    delivered_quantity_usd = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    delivered_quantity = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    entitlement_quantity_usd = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    entitlement_date = models.DateTimeField(blank=True, null=True)
    status_date = models.DateTimeField(blank=True, null=True)
    is_removed = models.BooleanField(default=False)
    conflicted = models.BooleanField(default=False)

    business_area = models.ForeignKey(BusinessArea, on_delete=models.DO_NOTHING, db_column="business_area_id")
    program = models.ForeignKey(HopeProgram, on_delete=models.DO_NOTHING, db_column="program_id", blank=True, null=True)
    delivery_type = models.ForeignKey(
        DeliveryMechanism, on_delete=models.DO_NOTHING, db_column="delivery_type_id", blank=True, null=True
    )
    financial_service_provider = models.ForeignKey(
        FinancialServiceProvider,
        on_delete=models.DO_NOTHING,
        db_column="financial_service_provider_id",
        blank=True,
        null=True,
    )
    household = models.ForeignKey(
        Household, on_delete=models.DO_NOTHING, db_column="household_id", blank=True, null=True
    )
    payment_plan = models.ForeignKey(
        PaymentPlan, on_delete=models.DO_NOTHING, db_column="parent_id", blank=True, null=True
    )

    class Meta:
        db_table = "payment_payment"

    def __str__(self) -> str:
        return f"Payment {self.id}"


class PaymentVerification(HopeModel):
    id = models.UUIDField(primary_key=True)
    status = models.CharField(max_length=50)
    payment = models.ForeignKey(
        Payment, on_delete=models.DO_NOTHING, db_column="payment_id", related_name="verifications"
    )

    class Meta:
        db_table = "payment_paymentverification"

    def __str__(self) -> str:
        return f"Verification {self.id}"
