from app.repositories import user_repositories

from app.schemas.user import OrderAddress , OrderAddressResponse
from app.schemas.base import BaseResponse

from fastapi import status, HTTPException
from datetime import datetime, timezone

from app.core.hashing import Hash

from app.schemas.user import (
    User as UserSchema,
    ShowUser,
    ResponseUser,
    OrderAddress
)

from app.schemas.base import BaseResponse, Meta
from app.core.context import get_request_id

async def create_new_user(db, payload):
    user = await user_repositories.get_user(db, email=payload.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    data = {
        "name":payload.name,
        "email":payload.email,
        "password":Hash.hash(payload.password),
        "dob":payload.dob,
        'mobile':payload.mobile,
        "gender":payload.gender,
        "role":payload.role
    }
    new_user = await user_repositories.create_user(db, data)

    return ResponseUser(
        status=status.HTTP_201_CREATED,
        success=True,
        message="User created successfully",
        lang="en",
        data=ShowUser(
            name=new_user.name,
            email=new_user.email,
            mobile=new_user.mobile,
            dob=new_user.dob,
            gender=new_user.gender,
            role=new_user.role
        ),
        meta=Meta(
            request_id=get_request_id(),
            timestamp = datetime.now(tz=timezone.utc)
        )
    )


async def create_new_session(db,request, user_id, refresh_token, expire):
    # Extract device info
    ip_address = request.headers.get(
        "x-forwarded-for", request.client.host
    )
    user_agent = request.headers.get("user-agent")

    session = {
        "user_id":user_id,
        "refresh_token":refresh_token,
        "device_name":"unknown",
        "device_type":"unknown",
        "ip_address":ip_address,
        "user_agent":user_agent,
        "expires_at":expire,
        "is_revoked":False,
        "created_at":datetime.now(timezone.utc),
        "last_used_at":datetime.now(timezone.utc)
    }

    session = await user_repositories.create_session(db, session)
    return session


def add_address(db, payload:OrderAddress, user_id):
    address = {
        "user_id": user_id,
        "district": payload.district,
        "address": payload.address,
        "landmark": payload.landmark,
        "recipient_name": payload.recipient_name,
        "recipient_contact": payload.recipient_contact,
        "recipient_backup_contact":payload.recipient_backup_contact,
        "address_category": payload.address_category,
        "default_shipping_address": payload.default_shipping_address,
        "default_billing_address":payload.default_billing_address
    }

    is_added =  user_repositories.add_address(db, address)
    addresses = user_repositories.get_all_address(db, user_id)
    addresses = [
        OrderAddress(
            district=address.district,
            address = address.address,
            landmark= address.landmark,
            recipient_name=address.recipient_name,
            recipient_contact=address.recipient_contact,
            recipient_backup_contact=address.recipient_backup_contact,

            address_category=address.address_category,
            default_shipping_address=address.default_shipping_address,
            default_billing_address=address.default_billing_address
        ) for address in addresses
    ]
    return OrderAddressResponse(
        status=status.HTTP_201_CREATED,
        message="Address Added Successfully",
        success=True,
        lang='en',
        data=addresses,
        meta=Meta(
                    request_id=get_request_id(),
                    timestamp = datetime.now(tz=timezone.utc)
                )
    )

def remove_address(db, address_id):
    is_removed = user_repositories.remove_address(db, address_id)
    if is_removed:
        return BaseResponse(
            status=status.HTTP_200_OK,
            message=f"address with id: {address_id} removed successfully",
            success=True,
            lang='en',
            data = [],
            meta=Meta(
                        request_id=get_request_id(),
                        timestamp = datetime.now(tz=timezone.utc)
                    )
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'address with id: {address_id} not found')

def get_all_adddress(db, user_id):
    addresses = user_repositories.get_all_address(db, user_id)
    addresses = [
        OrderAddress(
            district=address.district,
            address = address.address,
            landmark= address.landmark,
            recipient_name=address.recipient_name,
            recipient_contact=address.recipient_contact,
            recipient_backup_contact=address.recipient_backup_contact,

            address_category=address.address_category,
            default_shipping_address=address.default_shipping_address,
            default_billing_address=address.default_billing_address
        ) for address in addresses
    ]
    return OrderAddressResponse(
        status=status.HTTP_201_CREATED,
        message="Address Added Successfully",
        success=True,
        lang='en',
        data=addresses,
        meta=Meta(
                    request_id=get_request_id(),
                    timestamp = datetime.now(tz=timezone.utc)
                )
    )

def get_address(db, address_id):
    address = user_repositories.get_address(db, address_id)
    return OrderAddressResponse(
        status=status.HTTP_200_OK,
        message='success',
        success=True,
        lang='en',
        data = [
            OrderAddress(
            district=address.district,
            address = address.address,
            landmark= address.landmark,
            recipient_name=address.recipient_name,
            recipient_contact=address.recipient_contact,
            recipient_backup_contact=address.recipient_backup_contact,

            address_category=address.address_category,
            default_shipping_address=address.default_shipping_address,
            default_billing_address=address.default_billing_address
        )
        ],
        meta=Meta(
                    request_id=get_request_id(),
                    timestamp = datetime.now(tz=timezone.utc)
                )
    )

def update_address(db,payload, address_id):
    address = user_repositories.update_address(db, payload, address_id)
    return OrderAddressResponse(
        status=status.HTTP_200_OK,
        message='success',
        success=True,
        lang='en',
        data = [
            OrderAddress(
            district=address.district,
            address = address.address,
            landmark= address.landmark,
            recipient_name=address.recipient_name,
            recipient_contact=address.recipient_contact,
            recipient_backup_contact=address.recipient_backup_contact,

            address_category=address.address_category,
            default_shipping_address=address.default_shipping_address,
            default_billing_address=address.default_billing_address
        )
        ],
        meta=Meta(
                    request_id=get_request_id(),
                    timestamp = datetime.now(tz=timezone.utc)
                )
    )