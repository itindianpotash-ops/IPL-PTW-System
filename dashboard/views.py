from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from permits.models import Permit


@login_required
def home(request):

    if request.user.role == "SAFETY":

        total = Permit.objects.count()

        pending = Permit.objects.filter(
            status__in=[
                Permit.Status.SUBMITTED,
                Permit.Status.RESUBMITTED,
            ]
        ).count()

        approved = Permit.objects.filter(
            status=Permit.Status.APPROVED
        ).count()

        rejected = Permit.objects.filter(
            status=Permit.Status.REJECTED
        ).count()

        recent = Permit.objects.all()[:10]

    else:

        total = Permit.objects.filter(
            requester=request.user
        ).count()

        pending = Permit.objects.filter(
            requester=request.user,
            status__in=[
                Permit.Status.SUBMITTED,
                Permit.Status.RESUBMITTED,
            ],
        ).count()

        approved = Permit.objects.filter(
            requester=request.user,
            status=Permit.Status.APPROVED,
        ).count()

        rejected = Permit.objects.filter(
            requester=request.user,
            status=Permit.Status.REJECTED,
        ).count()

        recent = Permit.objects.filter(
            requester=request.user
        )[:10]

    return render(
        request,
        "dashboard/home.html",
        {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "recent": recent,
        },
    )
