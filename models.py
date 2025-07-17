from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Union, List, Literal
from datetime import datetime, timezone
from enum import Enum
from bson import ObjectId  

# User Model (unchanged)
class User(BaseModel):
    username: str
    email: str
    password: str
    role: str = ""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    bio: Optional[str] = None

# Item Type Enum
class ItemType(str, Enum):
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    PLACE = "place"

# Base Item Model
class BaseItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: ItemType
    location: str
    description: str
    rating: float = Field(ge=0, le=5)
    images: List[str] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Type-Specific Models
class HotelInfo(BaseModel):
    starRating: int = Field(ge=1, le=5, alias="hotelInfo")
    amenities: Dict[str, Union[str, bool, int]] = {}
    roomTypes: List[str] = []

class RestaurantInfo(BaseModel):
    cuisine: List[str]
    openingHours: str
    priceRange: Literal["$", "$$", "$$$"]

class PlaceInfo(BaseModel):
    category: str
    entranceFee: bool
    bestVisitingTime: str

# Main Item Model
class Item(BaseItem):
    # Backward compatible fields
    image: Optional[str] = Field(None, deprecated="Use 'images' list instead")
    amenities: Optional[Dict[str, Union[str, bool, int]]] = None
    hotelInfo: Optional[Dict[str, Union[str, int]]] = None
    
    # New structured fields
    hotelDetails: Optional[HotelInfo] = None
    restaurantDetails: Optional[RestaurantInfo] = None
    placeDetails: Optional[PlaceInfo] = None

    @field_validator('*', mode='before')
    @classmethod
    def handle_legacy_fields(cls, data):
        if isinstance(data, dict):
            # Migrate old hotelInfo to new structure
            if data.get('type') == "hotel" and 'hotelInfo' in data:
                if 'hotelDetails' not in data:
                    data['hotelDetails'] = {
                        'starRating': data['hotelInfo'].get('stars', 3),
                        'amenities': data.get('amenities', {})
                    }
            # Migrate single image to images list
            if 'image' in data and 'images' not in data:
                data['images'] = [data['image']] if data['image'] else []
        return data

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid)  # Now properly defined
        },
        arbitrary_types_allowed=True  # Allows ObjectId in model_dump()
    )