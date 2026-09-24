from fastapi import APIRouter

from src.router.payment_router.ecpay import ECPAY_ROUTER

PAYMENT_ROUTER = APIRouter(prefix="/payment")

PAYMENT_ROUTER.include_router(ECPAY_ROUTER)
