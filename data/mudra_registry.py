"""
data/mudra_registry.py — Classical Hasta Mudra Registry
Defines the canonical 28 Asamyuta (single-hand) Hasta Mudras according to
the Abhinaya Darpana and Natyashastra traditions.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class MudraInfo:
    name: str
    sanskrit: str
    description: str
    significance: str
    instructions: str = ""
    category: str = "Asamyuta"
    image_ref: Optional[str] = None
    finger_pattern: List[Optional[bool]] = field(default_factory=list)

    @property
    def meaning(self) -> str:
        return self.significance


_MUDRA_REGISTRY: List[MudraInfo] = [
    MudraInfo(
        name="Pataka",
        sanskrit="पताका",
        description="All four fingers extended straight together, thumb bent touching the base of the index finger.",
        significance="Flag, beginning of dance, clouds, forest, river, night, peace, open sky.",
        instructions="Keep the four fingers upright and touching each other firmly without bending. Fold the thumb against the palm.",
        category="Asamyuta",
        image_ref="pataka.png",
        finger_pattern=[False, True, True, True, True],
    ),
    MudraInfo(
        name="Tripataka",
        sanskrit="त्रिपताका",
        description="Three fingers extended upright, ring finger bent forward at the second knuckle, thumb bent.",
        significance="Crown, tree branches, thunderbolt, arrow, Indra, raising a flag.",
        instructions="Form Pataka, then bend the ring finger downward at the joint while keeping index, middle, and pinky upright.",
        category="Asamyuta",
        image_ref="tripataka.png",
        finger_pattern=[False, True, True, False, True],
    ),
    MudraInfo(
        name="Ardhapataka",
        sanskrit="अर्धपताका",
        description="Index and middle fingers extended together upright, ring and pinky bent into palm.",
        significance="Half flag, knife, dagger, shore of a river, leaves, horn.",
        instructions="Hold index and middle fingers straight together. Fold ring finger and pinky firmly against the palm with thumb resting over them.",
        category="Asamyuta",
        image_ref="ardhapataka.png",
        finger_pattern=[False, True, True, False, False],
    ),
    MudraInfo(
        name="Kartarimukha",
        sanskrit="कर्तरीमुख",
        description="Index and pinky fingers extended upright, middle and ring fingers bent touching thumb.",
        significance="Scissors, separation of lovers, lightning, death, footsteps, falling.",
        instructions="Extend the index finger and pinky finger like a pair of open shears. Bend the middle and ring fingers down.",
        category="Asamyuta",
        image_ref="kartarimukha.png",
        finger_pattern=[False, True, False, False, True],
    ),
    MudraInfo(
        name="Mayura",
        sanskrit="मयूर",
        description="Thumb and ring fingertip joined together, while index, middle, and pinky remain extended.",
        significance="Peacock neck, applying vermilion (tilak), wiping tears, beauty.",
        instructions="Touch the tip of the ring finger with the tip of the thumb. Keep index, middle, and little finger extended.",
        category="Asamyuta",
        image_ref="mayura.png",
        finger_pattern=[True, True, True, False, True],
    ),
    MudraInfo(
        name="Ardhachandra",
        sanskrit="अर्धचन्द्र",
        description="All four fingers joined and extended straight, thumb stretched sideways perpendicular to palm.",
        significance="Crescent moon, spear, seizing by the throat, consecrated plate.",
        instructions="Keep all four fingers extended together. Stretch the thumb outward to form a distinct crescent arch with the index finger.",
        category="Asamyuta",
        image_ref="ardhachandra.png",
        finger_pattern=[True, True, True, True, True],
    ),
    MudraInfo(
        name="Arala",
        sanskrit="अराल",
        description="Index finger curved like a bow, thumb bent, while middle, ring, and pinky fingers remain extended upright.",
        significance="Drinking nectar (amrita), violent wind, poison, blessing.",
        instructions="Extend middle, ring, and pinky fingers upright together. Curve the index finger into a bow shape.",
        category="Asamyuta",
        image_ref="arala.png",
        finger_pattern=[False, False, True, True, True],
    ),
    MudraInfo(
        name="Shukatunda",
        sanskrit="शुकतुण्ड",
        description="Index and ring fingers curved downward like a beak, while thumb, middle, and pinky are positioned.",
        significance="Parrot beak, shooting an arrow, mystery, ferocity.",
        instructions="Bend the tip of the index finger sharply inward resembling a parrot's curved beak.",
        category="Asamyuta",
        image_ref="shukatunda.png",
        finger_pattern=[False, False, True, False, True],
    ),
    MudraInfo(
        name="Mushti",
        sanskrit="मुष्टि",
        description="All four fingers curled tightly into a fist, thumb pressed firmly over the fingers.",
        significance="Grasp, strength, wrestling, holding weapons, steadfastness.",
        instructions="Curl all four fingers into the palm to form a tight fist. Place the thumb over the fingers.",
        category="Asamyuta",
        image_ref="mushti.png",
        finger_pattern=[False, False, False, False, False],
    ),
    MudraInfo(
        name="Shikhara",
        sanskrit="शिखर",
        description="Four fingers curled into a fist, thumb held strictly upright pointing toward the sky.",
        significance="Spire, hero, deity Shiva, bow, bell, firmness, questioning.",
        instructions="Form a fist with fingers curled in, then extend the thumb erect and pointing straight up.",
        category="Asamyuta",
        image_ref="shikhara.png",
        finger_pattern=[True, False, False, False, False],
    ),
    MudraInfo(
        name="Kapittha",
        sanskrit="कपित्थ",
        description="Thumb pressed against the bent index finger, while middle, ring, and little fingers are curled in.",
        significance="Goddess Lakshmi, holding cymbals, offering incense, milch cow.",
        instructions="Bend the index finger over the thumb tip, keeping the other three fingers closed into the palm.",
        category="Asamyuta",
        image_ref="kapittha.png",
        finger_pattern=[False, False, False, False, False],
    ),
    MudraInfo(
        name="Katakamukha",
        sanskrit="कटकामुख",
        description="Index and middle fingertips meet the thumb tip forming an opening; ring and pinky slightly raised.",
        significance="Plucking flowers, wearing a pearl necklace, drawing a bow, holding a mirror.",
        instructions="Bring the tips of the index and middle fingers to touch the tip of the thumb. Keep pinky and ring fingers raised.",
        category="Asamyuta",
        image_ref="katakamukha.png",
        finger_pattern=[True, True, True, False, True],
    ),
    MudraInfo(
        name="Suchi",
        sanskrit="सूची",
        description="Index finger pointing straight up, thumb resting over middle, ring, and pinky curled into palm.",
        significance="Needle, number one, pointing, Supreme Soul (Brahman), world, wheel.",
        instructions="Close middle, ring, and pinky fingers into the palm. Extend the index finger straight upright like an arrow.",
        category="Asamyuta",
        image_ref="suchi.png",
        finger_pattern=[False, True, False, False, False],
    ),
    MudraInfo(
        name="Chandrakala",
        sanskrit="चन्द्रकला",
        description="Thumb and index finger extended wide apart forming a crescent shape, remaining fingers curled into palm.",
        significance="Crescent moon, crown of Shiva, Ganga, measuring crescent width.",
        instructions="Extend thumb and index finger outward to create a clear crescent span, curling middle, ring, and pinky fingers in.",
        category="Asamyuta",
        image_ref="chandrakala.png",
        finger_pattern=[True, True, False, False, False],
    ),
    MudraInfo(
        name="Padmakosha",
        sanskrit="पद्मकोश",
        description="All five fingers spread and gently curved inward forming the shape of a lotus bud.",
        significance="Lotus bud, apple, mango, circular movement, offering flowers, egg.",
        instructions="Cup the palm slightly and curve all five fingers inward without allowing the fingertips to touch.",
        category="Asamyuta",
        image_ref="padmakosha.png",
        finger_pattern=[True, True, True, True, True],
    ),
    MudraInfo(
        name="Sarpasirah",
        sanskrit="सर्पशिरः",
        description="All fingers extended together with the palm cupped hollow, mimicking a serpent's hood.",
        significance="Serpent hood, offering water, splashing water, cobra.",
        instructions="Keep all fingers joined together like Pataka, but cup the palm deeply to create a hollow serpent hood contour.",
        category="Asamyuta",
        image_ref="sarpasirah.png",
        finger_pattern=[False, True, True, True, True],
    ),
    MudraInfo(
        name="Mrigashirsha",
        sanskrit="मृगशीर्ष",
        description="Thumb and pinky fingers extended upright, while index, middle, and ring fingers are bent forward.",
        significance="Deer head, flute, cheek, costume, stepping softly, forest animal.",
        instructions="Extend the thumb and pinky finger like deer ears. Bend middle, ring, and index fingers forward horizontally.",
        category="Asamyuta",
        image_ref="mrigashirsha.png",
        finger_pattern=[True, False, False, False, True],
    ),
    MudraInfo(
        name="Simhamukha",
        sanskrit="सिंहमुख",
        description="Thumb, index, and pinky extended; middle and ring fingers bent forward touching or near thumb.",
        significance="Lion face, pearl, haoma sacrifice, bravery, medicinal herb.",
        instructions="Extend index and little fingers upright. Bend middle and ring fingers toward the thumb tip to suggest lion ears and muzzle.",
        category="Asamyuta",
        image_ref="simhamukha.png",
        finger_pattern=[True, True, False, False, True],
    ),
    MudraInfo(
        name="Kangula",
        sanskrit="कंगुल",
        description="Ring finger bent into the palm while thumb, index, and middle fingers are extended slightly curved.",
        significance="Areca nut, bell fruit, water lily, infant, bird.",
        instructions="Fold the ring finger down into the palm while keeping thumb, index, and middle extended forward.",
        category="Asamyuta",
        image_ref="kangula.png",
        finger_pattern=[True, True, True, False, True],
    ),
    MudraInfo(
        name="Alapadma",
        sanskrit="अलपद्म",
        description="All five fingers spread out wide and curled outwards sequentially like an open lotus flower.",
        significance="Full-blown lotus, beauty, circular motion, mirror, full moon, hair knot.",
        instructions="Spread every finger as wide apart as possible, curling the pinky outward the most to resemble open petals.",
        category="Asamyuta",
        image_ref="alapadma.png",
        finger_pattern=[True, True, True, True, True],
    ),
    MudraInfo(
        name="Chatura",
        sanskrit="चतुर",
        description="Thumb held across the palm touching the base of the middle finger, other four fingers extended close together.",
        significance="Gold, copper, intelligence, oil, small quantity, sweet conversation.",
        instructions="Extend four fingers straight together. Position the thumb flat against the palm under the middle finger.",
        category="Asamyuta",
        image_ref="chatura.png",
        finger_pattern=[False, True, True, True, True],
    ),
    MudraInfo(
        name="Bhramara",
        sanskrit="भ्रमर",
        description="Index finger curled tightly touching the thumb joint, middle finger extended, ring and pinky curved.",
        significance="Black bee, winged insect, silent flight, gathering honey.",
        instructions="Bend the index finger to press the inner crease of the thumb. Keep the middle finger straight and others curved.",
        category="Asamyuta",
        image_ref="bhramara.png",
        finger_pattern=[False, False, True, False, False],
    ),
    MudraInfo(
        name="Hamsasya",
        sanskrit="हंसास्य",
        description="Tip of index finger touching tip of thumb forming a delicate ring, middle, ring, and pinky extended straight.",
        significance="Swan beak, tying a sacred thread, painting, initiation, delicate pearl.",
        instructions="Pinch index fingertip and thumb tip together precisely. Extend middle, ring, and pinky fingers upright and relaxed.",
        category="Asamyuta",
        image_ref="hamsasya.png",
        finger_pattern=[True, True, True, True, True],
    ),
    MudraInfo(
        name="Hamsapaksha",
        sanskrit="हंसपक्ष",
        description="Pinky finger extended upright, thumb bent, while index, middle, and ring fingers are gently graduated.",
        significance="Swan wing, number six, building a bridge, covering.",
        instructions="Extend four fingers together with the pinky elevated slightly higher than the rest, thumb tucked in.",
        category="Asamyuta",
        image_ref="hamsapaksha.png",
        finger_pattern=[False, True, True, True, True],
    ),
    MudraInfo(
        name="Sandamsha",
        sanskrit="संदंश",
        description="Thumb and index fingertips repeatedly touch and open like pincers, with other fingers cupped.",
        significance="Pincers, counting, small gift, throbbing heart, offering.",
        instructions="Repeatedly bring the index and thumb fingertips together like a gentle pincer.",
        category="Asamyuta",
        image_ref="sandamsha.png",
        finger_pattern=[True, True, True, True, True],
    ),
    MudraInfo(
        name="Mukula",
        sanskrit="मुकुल",
        description="All five fingertips brought together to touch at a single central point like a flower bud.",
        significance="Flower bud, eating, lotus bud, water lily, kissing, small gift.",
        instructions="Bring all five fingertips (thumb, index, middle, ring, pinky) to meet together tightly at a single point.",
        category="Asamyuta",
        image_ref="mukula.png",
        finger_pattern=[True, True, True, True, True],
    ),
    MudraInfo(
        name="Tamrachuda",
        sanskrit="ताम्रचूड",
        description="Index finger hooked like a rooster's crest, thumb touching middle finger, ring and pinky folded.",
        significance="Rooster, crane, camel, calf, writing.",
        instructions="Curve the index finger sharply forward like a hook while curling other fingers in.",
        category="Asamyuta",
        image_ref="tamrachuda.png",
        finger_pattern=[False, False, False, False, False],
    ),
    MudraInfo(
        name="Trishula",
        sanskrit="त्रिशूल",
        description="Index, middle, and ring fingers extended straight and separated, while thumb holds down the pinky.",
        significance="Trident of Shiva, three worlds (triloka), holy trinity, sacred leaf.",
        instructions="Hold index, middle, and ring fingers straight up like the three prongs of a trident. Lock the pinky down with the thumb.",
        category="Asamyuta",
        image_ref="trishula.png",
        finger_pattern=[False, True, True, True, False],
    ),
]


def get_all_mudras() -> List[MudraInfo]:
    return _MUDRA_REGISTRY


def get_mudra_by_name(name: str) -> Optional[MudraInfo]:
    name_lower = name.strip().lower()
    for m in _MUDRA_REGISTRY:
        if m.name.lower() == name_lower or m.sanskrit.lower() == name_lower:
            return m
    return None


def get_mudra_names() -> List[str]:
    return sorted(m.name for m in _MUDRA_REGISTRY)


def get_mudras_by_category(category: str) -> List[MudraInfo]:
    return [m for m in _MUDRA_REGISTRY if m.category.lower() == category.lower()]
