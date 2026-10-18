from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models.website_visit import WebsiteVisit
from app.schemas.website_visit import WebsiteVisitCreate


router = APIRouter(
    prefix="/website-visits",
    tags=["Website Visits"],
)


@router.post("/visits", status_code=status.HTTP_201_CREATED)
def create_website_visit(
    payload: WebsiteVisitCreate,
    request: Request,
):
    ip_address = request.client.host if request.client else None

    visit = WebsiteVisit(
        site_key=payload.site_key,
        visitor_id=payload.visitor_id,
        page_path=payload.page_path,
        ip_address=ip_address,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
    )

    try:
        with SessionLocal() as session:
            session.add(visit)
            session.commit()
            session.refresh(visit)

            return {
                "id": visit.id,
                "status": "recorded",
            }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to record website visit",
        )