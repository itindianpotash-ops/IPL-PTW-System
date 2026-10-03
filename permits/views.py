

from django.contrib.auth.decorators import login_required
from django.http import  JsonResponse

from audit.models import AuditLog
from master.models import (
    PermitType,
    PermitTypePPE,
    PermitTypeSafetyControl,
)

from .forms import PermitForm, ReviewForm
from .models import (
    Permit,
    PermitPPE,
    PermitReview,
    PermitSafetyControl,
)


def create_audit(
    user,
    action,
    obj,
    description="",
):

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=obj.__class__.__name__,
        object_id=str(obj.pk),
        description=description,
    )


@login_required
def permit_list(request):

    if request.user.role == "SAFETY":
        permits = Permit.objects.all()

    elif request.user.role == "ADMIN":
        permits = Permit.objects.all()

    else:
        permits = Permit.objects.filter(
            requester=request.user
        )

    return render(
        request,
        "permits/list.html",
        {
            "permits": permits,
        },
    )




# @login_required
# def permit_list(request):
#
#     # ==========================================
#     # ADMIN
#     # ==========================================
#
#     if request.user.role == "ADMIN":
#
#         permits = (
#             Permit.objects
#             .select_related(
#                 "permit_type",
#                 "location",
#                 "requester",
#                 "approved_by",
#             )
#             .prefetch_related(
#                 "ppe_items__ppe",
#                 "safety_controls__safety_control",
#             )
#             .order_by("-created_at")
#         )
#
#
#     # ==========================================
#     # SAFETY OFFICER
#     # ==========================================
#
#     elif request.user.role == "SAFETY":
#
#         permits = (
#             Permit.objects
#             .select_related(
#                 "permit_type",
#                 "location",
#                 "requester",
#                 "approved_by",
#             )
#             .prefetch_related(
#                 "ppe_items__ppe",
#                 "safety_controls__safety_control",
#             )
#             .order_by("-created_at")
#         )
#
#
#     # ==========================================
#     # NORMAL USER / REQUESTER
#     # ==========================================
#
#     else:
#
#         permits = (
#             Permit.objects
#             .filter(
#                 requester=request.user
#             )
#             .select_related(
#                 "permit_type",
#                 "location",
#                 "requester",
#                 "approved_by",
#             )
#             .prefetch_related(
#                 "ppe_items__ppe",
#                 "safety_controls__safety_control",
#             )
#             .order_by("-created_at")
#         )
#
#
#     return render(
#         request,
#         "permits/list.html",
#         {
#             "permits": permits,
#         },
#     )

@login_required
def permit_create(request):

    if request.method == "POST":

        form = PermitForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                permit = form.save(commit=False)

                permit.requester = request.user
                permit.status = Permit.Status.SUBMITTED

                permit.save()

                # Copy PPE configuration
                ppe_configurations = (
                    PermitTypePPE.objects
                    .filter(
                        permit_type=permit.permit_type
                    )
                    .select_related("ppe")
                )

                for config in ppe_configurations:

                    PermitPPE.objects.create(
                        permit=permit,
                        ppe=config.ppe,
                        required=config.required,
                    )

                # Copy safety-control configuration
                control_configurations = (
                    PermitTypeSafetyControl.objects
                    .filter(
                        permit_type=permit.permit_type
                    )
                    .select_related("safety_control")
                )

                for config in control_configurations:

                    PermitSafetyControl.objects.create(
                        permit=permit,
                        safety_control=config.safety_control,
                        required=config.required,
                    )

                create_audit(
                    request.user,
                    "SUBMITTED",
                    permit,
                    "Permit submitted for safety review.",
                )

            messages.success(
                request,
                f"{permit.permit_number} submitted successfully.",
            )

            return redirect(
                "permit_detail",
                pk=permit.pk,
            )

    else:

        form = PermitForm()

    return render(
        request,
        "permits/create.html",
        {
            "form": form,
        },
    )


@login_required
def permit_detail(request, pk):

    permit = get_object_or_404(
        Permit.objects.select_related(
            "permit_type",
            "location",
            "requester",
            "approved_by",
        ),
        pk=pk,
    )

    if (
        request.user.role not in ["ADMIN", "SAFETY"]
        and permit.requester != request.user
    ):
        return HttpResponseForbidden(
            "You do not have permission to view this permit."
        )

    return render(
        request,
        "permits/detail.html",
        {
            "permit": permit,
        },
    )


@login_required
def permit_edit(request, pk):

    permit = get_object_or_404(
        Permit,
        pk=pk,
    )

    if permit.requester != request.user:
        return HttpResponseForbidden()

    if permit.status not in [
        Permit.Status.REJECTED,
        Permit.Status.DRAFT,
    ]:
        messages.error(
            request,
            "Only rejected or draft permits can be edited.",
        )

        return redirect(
            "permit_detail",
            pk=permit.pk,
        )

    if request.method == "POST":

        form = PermitForm(
            request.POST,
            instance=permit,
        )

        if form.is_valid():

            with transaction.atomic():

                permit = form.save(commit=False)

                permit.status = Permit.Status.RESUBMITTED
                permit.rejection_reason = ""

                permit.save()

                create_audit(
                    request.user,
                    "RESUBMITTED",
                    permit,
                    "Rejected permit edited and resubmitted.",
                )

            messages.success(
                request,
                "Permit resubmitted for review.",
            )

            return redirect(
                "permit_detail",
                pk=permit.pk,
            )

    else:

        form = PermitForm(
            instance=permit,
        )

    return render(
        request,
        "permits/create.html",
        {
            "form": form,
            "editing": True,
            "permit": permit,
        },
    )


# @login_required
# def permit_review(request, pk):
#
#     if request.user.role != "SAFETY":
#         return HttpResponseForbidden(
#             "Only Safety Officers can review permits."
#         )
#
#     permit = get_object_or_404(
#         Permit,
#         pk=pk,
#     )
#
#     if permit.status not in [
#         Permit.Status.SUBMITTED,
#         Permit.Status.RESUBMITTED,
#     ]:
#         messages.error(
#             request,
#             "This permit is not awaiting review.",
#         )
#
#         return redirect(
#             "permit_detail",
#             pk=permit.pk,
#         )
#
#     if request.method == "POST":
#
#         form = ReviewForm(request.POST)
#
#         if form.is_valid():
#
#             action = request.POST.get("action")
#             remarks = form.cleaned_data["remarks"]
#
#             if action == "APPROVE":
#
#                 required_ppe = permit.ppe_items.filter(
#                     required=True
#                 )
#
#                 required_controls = permit.safety_controls.filter(
#                     required=True
#                 )
#
#                 if required_ppe.filter(
#                     verified=False
#                 ).exists():
#
#                     messages.error(
#                         request,
#                         "All required PPE must be verified.",
#                     )
#
#                     return redirect(
#                         "permit_review",
#                         pk=permit.pk,
#                     )
#
#                 if required_controls.filter(
#                     verified=False
#                 ).exists():
#
#                     messages.error(
#                         request,
#                         "All required safety controls must be verified.",
#                     )
#
#                     return redirect(
#                         "permit_review",
#                         pk=permit.pk,
#                     )
#
#                 permit.status = Permit.Status.APPROVED
#                 permit.approved_by = request.user
#                 permit.approved_at = timezone.now()
#
#                 permit.save()
#
#                 PermitReview.objects.create(
#                     permit=permit,
#                     safety_officer=request.user,
#                     action=PermitReview.Action.APPROVE,
#                     remarks=remarks,
#                 )
#
#                 create_audit(
#                     request.user,
#                     "APPROVED",
#                     permit,
#                     remarks,
#                 )
#
#                 messages.success(
#                     request,
#                     "Permit approved.",
#                 )
#
#                 return redirect(
#                     "permit_detail",
#                     pk=permit.pk,
#                 )
#
#             elif action == "REJECT":
#
#                 if not remarks.strip():
#
#                     messages.error(
#                         request,
#                         "Remarks are required when rejecting a permit.",
#                     )
#
#                     return redirect(
#                         "permit_review",
#                         pk=permit.pk,
#                     )
#
#                 permit.status = Permit.Status.REJECTED
#                 permit.rejection_reason = remarks
#
#                 permit.save()
#
#                 PermitReview.objects.create(
#                     permit=permit,
#                     safety_officer=request.user,
#                     action=PermitReview.Action.REJECT,
#                     remarks=remarks,
#                 )
#
#                 create_audit(
#                     request.user,
#                     "REJECTED",
#                     permit,
#                     remarks,
#                 )
#
#                 messages.warning(
#                     request,
#                     "Permit rejected.",
#                 )
#
#                 return redirect(
#                     "permit_detail",
#                     pk=permit.pk,
#                 )
#
#     else:
#
#         form = ReviewForm()
#
#     return render(
#         request,
#         "permits/review.html",
#         {
#             "permit": permit,
#             "form": form,
#         },
#     )


@login_required
def verify_ppe(request, pk):

    if request.user.role != "SAFETY":
        return HttpResponseForbidden()

    item = get_object_or_404(
        PermitPPE,
        pk=pk,
    )

    item.verified = request.POST.get("verified") == "true"

    item.remarks = request.POST.get(
        "remarks",
        "",
    )

    item.save()

    return redirect(
        "permit_review",
        pk=item.permit.pk,
    )


@login_required
def verify_control(request, pk):

    if request.user.role != "SAFETY":
        return HttpResponseForbidden()

    item = get_object_or_404(
        PermitSafetyControl,
        pk=pk,
    )

    item.verified = request.POST.get("verified") == "true"

    item.remarks = request.POST.get(
        "remarks",
        "",
    )

    item.save()

    return redirect(
        "permit_review",
        pk=item.permit.pk,
    )


@login_required
def permit_pdf(request, pk):

    permit = get_object_or_404(
        Permit,
        pk=pk,
    )

    if permit.status != Permit.Status.APPROVED:
        messages.error(
            request,
            "Only approved permits can generate PDF."
        )

        return redirect(
            "permit_detail",
            pk=permit.pk,
        )

    from .pdf import generate_permit_pdf

    return generate_permit_pdf(
        request,
        permit,
    )

@login_required
def permit_type_configuration(request, pk):

    permit_type = get_object_or_404(
        PermitType,
        pk=pk,
        active=True,
    )

    ppe_configurations = (
        PermitTypePPE.objects
        .filter(
            permit_type=permit_type,
            ppe__active=True,
        )
        .select_related("ppe")
    )

    control_configurations = (
        PermitTypeSafetyControl.objects
        .filter(
            permit_type=permit_type,
            safety_control__active=True,
        )
        .select_related("safety_control")
    )

    data = {
        "permit_type": {
            "id": permit_type.id,
            "name": permit_type.name,
            "code": permit_type.code,
            "description": permit_type.description,
        },

        "ppe": [
            {
                "id": item.ppe.id,
                "name": item.ppe.name,
                "code": item.ppe.code,
                "description": item.ppe.description,
                "required": item.required,
            }
            for item in ppe_configurations
        ],

        "safety_controls": [
            {
                "id": item.safety_control.id,
                "name": item.safety_control.name,
                "description": item.safety_control.description,
                "required": item.required,
            }
            for item in control_configurations
        ],
    }

    return JsonResponse(data)

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

@login_required()
def permit_review(request, pk):

    # ==================================================
    # SAFETY OFFICER CHECK
    # ==================================================

    if request.user.role != "SAFETY":

        return HttpResponseForbidden(
            "Only Safety Officers can review permits."
        )


    # ==================================================
    # GET PERMIT
    # ==================================================

    permit = get_object_or_404(
        Permit,
        pk=pk,
    )


    # ==================================================
    # CHECK PERMIT STATUS
    # ==================================================

    if permit.status not in [
        Permit.Status.SUBMITTED,
        Permit.Status.RESUBMITTED,
    ]:

        messages.error(
            request,
            "This permit is not awaiting review.",
        )

        return redirect(
            "permit_detail",
            pk=permit.pk,
        )


    # ==================================================
    # POST
    # ==================================================

    if request.method == "POST":

        form = ReviewForm(request.POST)


        if form.is_valid():

            action = request.POST.get(
                "action"
            )

            remarks = form.cleaned_data.get(
                "remarks",
                ""
            ).strip()


            # ==========================================
            # GET VERIFIED PPE IDS
            # ==========================================

            verified_ppe_ids = {
                int(pk)
                for pk in request.POST.getlist(
                    "ppe_verified"
                )
            }


            # ==========================================
            # GET VERIFIED CONTROL IDS
            # ==========================================

            verified_control_ids = {
                int(pk)
                for pk in request.POST.getlist(
                    "control_verified"
                )
            }


            # ==========================================
            # ATOMIC TRANSACTION
            # ==========================================

            with transaction.atomic():

                # --------------------------------------
                # LOCK PERMIT
                # --------------------------------------

                permit = (
                    Permit.objects
                    .select_for_update()
                    .get(pk=pk)
                )


                # --------------------------------------
                # CHECK AGAIN
                # --------------------------------------

                if permit.status not in [
                    Permit.Status.SUBMITTED,
                    Permit.Status.RESUBMITTED,
                ]:

                    messages.error(
                        request,
                        "This permit has already been reviewed.",
                    )

                    return redirect(
                        "permit_detail",
                        pk=permit.pk,
                    )


                # ======================================
                # PPE
                # ======================================

                ppe_items = list(
                    permit.ppe_items.all()
                )


                for item in ppe_items:

                    item.verified = (
                        item.pk in verified_ppe_ids
                    )


                    item.remarks = request.POST.get(
                        f"ppe_remarks_{item.pk}",
                        ""
                    ).strip()


                    # If your model has verified_by,
                    # keep this line.
                    item.verified_by = request.user


                    item.save()


                # ======================================
                # SAFETY CONTROLS
                # ======================================

                control_items = list(
                    permit.safety_controls.all()
                )


                for item in control_items:

                    item.verified = (
                        item.pk in verified_control_ids
                    )


                    item.remarks = request.POST.get(
                        f"control_remarks_{item.pk}",
                        ""
                    ).strip()


                    # If your model has verified_by,
                    # keep this line.
                    item.verified_by = request.user


                    item.save()


                # ======================================
                # APPROVE
                # ======================================

                if action == "APPROVE":

                    # ----------------------------------
                    # REQUIRED PPE
                    # ----------------------------------

                    missing_ppe = [
                        item
                        for item in ppe_items
                        if item.required
                        and not item.verified
                    ]


                    # ----------------------------------
                    # REQUIRED CONTROLS
                    # ----------------------------------

                    missing_controls = [
                        item
                        for item in control_items
                        if item.required
                        and not item.verified
                    ]


                    # ----------------------------------
                    # BLOCK APPROVAL
                    # ----------------------------------

                    if (
                        missing_ppe
                        or missing_controls
                    ):

                        messages.error(
                            request,
                            "All required PPE and safety "
                            "controls must be verified "
                            "before approval.",
                        )

                        return redirect(
                            "permit_review",
                            pk=permit.pk,
                        )


                    # ----------------------------------
                    # APPROVE PERMIT
                    # ----------------------------------

                    permit.status = (
                        Permit.Status.APPROVED
                    )

                    permit.approved_by = (
                        request.user
                    )

                    permit.approved_at = (
                        timezone.now()
                    )


                    permit.save()


                    # ----------------------------------
                    # REVIEW RECORD
                    # ----------------------------------

                    PermitReview.objects.create(
                        permit=permit,
                        safety_officer=request.user,
                        action=(
                            PermitReview.Action.APPROVE
                        ),
                        remarks=remarks,
                    )


                    # ----------------------------------
                    # AUDIT
                    # ----------------------------------

                    create_audit(
                        request.user,
                        "APPROVED",
                        permit,
                        remarks,
                    )


                    messages.success(
                        request,
                        "Permit approved successfully.",
                    )


                    return redirect(
                        "permit_detail",
                        pk=permit.pk,
                    )


                # ======================================
                # REJECT
                # ======================================

                elif action == "REJECT":

                    if not remarks:

                        messages.error(
                            request,
                            "Remarks are required when "
                            "rejecting a permit.",
                        )

                        return redirect(
                            "permit_review",
                            pk=permit.pk,
                        )


                    # ----------------------------------
                    # REJECT PERMIT
                    # ----------------------------------

                    permit.status = (
                        Permit.Status.REJECTED
                    )

                    permit.rejection_reason = remarks


                    permit.save()


                    # ----------------------------------
                    # REVIEW RECORD
                    # ----------------------------------

                    PermitReview.objects.create(
                        permit=permit,
                        safety_officer=request.user,
                        action=(
                            PermitReview.Action.REJECT
                        ),
                        remarks=remarks,
                    )


                    # ----------------------------------
                    # AUDIT
                    # ----------------------------------

                    create_audit(
                        request.user,
                        "REJECTED",
                        permit,
                        remarks,
                    )


                    messages.warning(
                        request,
                        "Permit rejected.",
                    )


                    return redirect(
                        "permit_detail",
                        pk=permit.pk,
                    )


                # ======================================
                # INVALID ACTION
                # ======================================

                else:

                    messages.error(
                        request,
                        "Invalid review action.",
                    )

                    return redirect(
                        "permit_review",
                        pk=permit.pk,
                    )


    # ==================================================
    # GET
    # ==================================================

    else:

        form = ReviewForm()


    # ==================================================
    # RENDER
    # ==================================================

    return render(
        request,
        "permits/review.html",
        {
            "permit": permit,
            "form": form,
        },
    )

