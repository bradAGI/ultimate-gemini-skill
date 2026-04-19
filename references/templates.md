# Prompt Templates

26 domain-specific prompt recipes, adapted from [`anand-92/ultimate-image-gen-mcp`](https://github.com/anand-92/ultimate-image-gen-mcp). Each gives a crafted prompt body plus the recommended `generate-image` params. Load this file only when the user's ask clearly maps to one of these domains.

## Contents

1. [photography_shot](#photography_shot) — photorealistic with lens + lighting specs
2. [logo_design](#logo_design) — brand identity
3. [cinematic_scene](#cinematic_scene) — film still, anamorphic
4. [product_mockup](#product_mockup) — commercial product
5. [batch_storyboard](#batch_storyboard) — multi-scene narrative (uses `batch_generate`)
6. [macro_shot](#macro_shot) — extreme macro
7. [fashion_portrait](#fashion_portrait) — editorial fashion
8. [technical_cutaway](#technical_cutaway) — Stephen Biesty style diagram
9. [flat_lay](#flat_lay) — overhead knolling
10. [action_freeze](#action_freeze) — high-speed strobe
11. [night_street](#night_street) — moody low-light
12. [drone_aerial](#drone_aerial) — top-down aerial
13. [stylized_3d_render](#stylized_3d_render) — UE5 character render
14. [sem_microscopy](#sem_microscopy) — false-color SEM
15. [double_exposure](#double_exposure) — blended silhouette
16. [architectural_viz](#architectural_viz) — archviz
17. [isometric_illustration](#isometric_illustration) — isometric 3D
18. [food_photography](#food_photography) — Michelin food
19. [motion_blur](#motion_blur) — rear-curtain sync
20. [typography_physical](#typography_physical) — environmental text
21. [retro_futurism](#retro_futurism) — analog sci-fi
22. [surreal_dreamscape](#surreal_dreamscape) — surrealist
23. [character_sheet](#character_sheet) — A-pose + 3/4 + action
24. [pbr_texture](#pbr_texture) — seamless texture map
25. [historical_photo](#historical_photo) — period piece
26. [bioluminescent_nature](#bioluminescent_nature) — glowing macro
27. [silhouette_shot](#silhouette_shot) — backlit silhouette

> Remember the user defaults: `image_size: "1K"` (override the `2K`/`4K` listed below only if the user explicitly asks for higher res); `21:9` is preferred for banners.

---

## photography_shot

**Prompt**: Photorealistic photograph of {subject}. Shot on a Sony α7R V with a 85mm f/1.4 prime lens. Aperture f/1.8 for creamy background separation. {Lighting} lighting — warm directional light casting long shadows with rich colour temperature. Shallow depth of field, ultra-sharp subject, smooth bokeh background. HDR tonal range, true-to-life skin tones, natural colour grading. Captured at eye level, rule-of-thirds composition. Professional editorial quality, no AI artefacts.

**Params**: `aspect_ratio: "16:9"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## logo_design

**Prompt**: {Style} logo design for "{brand_name}"{ for a {industry} company}. Primary colour: {primary_color}. Clean vector-style artwork, strong silhouette that works at any scale. Negative space used intentionally. Lettermark or wordmark — whichever suits the name best. Flat design with no gradients unless they serve the concept. Transparent or white background. Professional, timeless, instantly recognisable.

**Params**: `aspect_ratio: "1:1"` · `image_size: "4K"` · `response_modalities: ["IMAGE"]`

## cinematic_scene

**Prompt**: Cinematic film still of {subject} in {setting}. Mood: {mood}. Time of day: {time_of_day}. Shot on ARRI Alexa 35 with a 35mm anamorphic lens — characteristic horizontal lens flares. Colour grade: desaturated midtones with crushed blacks and a subtle warm highlight roll-off. Film grain at ISO 800. Shallow focus with deliberate rack-focus blur on background elements. Dramatic chiaroscuro lighting. Scene feels pulled from a prestige feature film — narrative tension, visual poetry.

**Params**: `aspect_ratio: "21:9"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## product_mockup

**Prompt**: High-end commercial product photograph of {product}. Background: {background}. {Hero shot — product centred, slightly elevated angle, bold and confident | Lifestyle context shot — product shown in natural use environment}. Studio strobe lighting with a large octabox key light and subtle fill reflector — no harsh shadows, clean specular highlights that reveal material texture. Colour-accurate rendering: true whites, saturated brand colours. Razor-sharp focus across the entire product. No props unless they reinforce brand story. Retouched to e-commerce/advertising standard — immaculate, aspirational.

**Params**: `aspect_ratio: "1:1"` (hero) or `"4:5"` (lifestyle) · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## batch_storyboard

Use `batch_generate`, not `generate_image`. Craft N distinct scene prompts (cap 8) that share characters / palette / art direction but vary camera angle, lighting, distance, and emotional beat.

**Params**: `aspect_ratio: "16:9"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]` · `prompts: [scene1, scene2, ...]`

## macro_shot

**Prompt**: Extreme macro photography of {subject}. Shot on a 100mm macro lens at f/2.8. Incredibly shallow depth of field. The focus is razor-sharp on {detail}, revealing microscopic textures, {texture_adjective} surfaces, and fine {material} details. Lighting is a single, hard micro-snoot from the {lighting_direction}, creating high-contrast micro-shadows. Background is a completely blurred out {background_color}.

**Params**: `aspect_ratio: "1:1"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## fashion_portrait

**Prompt**: Editorial fashion portrait of {subject}. Shot in a studio setup. Lighting features a harsh gobo projecting a shadow pattern of {shadow_pattern} across the subject's face and {background_material}. The subject is wearing {clothing} made of {material}, which catches the light. Hyper-detailed skin texture, visible pores, natural skin flaws. 85mm lens, f/8 for total sharpness.

**Params**: `aspect_ratio: "4:5"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## technical_cutaway

**Prompt**: A highly detailed, technical cutaway diagram of {object_system} in the intricate, hand-drawn style of Stephen Biesty. The drawing reveals the internal mechanics, {internal_element_1}, and {internal_element_2}. Clean white background, precise linework, watercolor shading, and neat, minimalist typography pointing to various components.

**Params**: `aspect_ratio: "3:2"` · `image_size: "4K"` · `response_modalities: ["IMAGE"]`

## flat_lay

**Prompt**: Flat lay overhead photography of {theme}. Arranged meticulously on a {surface} surface. The composition includes {props} arranged in a pleasing geometric grid (knolling). Soft, diffuse window light coming from the top left, creating long, soft shadows. High resolution, vibrant and color-coordinated palette centering around {colors}.

**Params**: `aspect_ratio: "1:1"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## action_freeze

**Prompt**: A dynamic, high-speed action shot of {subject} performing {action} in {location}. The subject is frozen perfectly in time, illuminated by a high-speed strobe flash, while the background exhibits severe motion blur to convey intense speed. Droplets/particles of {element} are suspended in mid-air, catching the rim light. Low angle, wide field of view.

**Params**: `aspect_ratio: "16:9"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## night_street

**Prompt**: A haunting, moody night street photograph of {location}. Shot on a 50mm lens at f/1.4 for excellent low-light gathering. The scene is illuminated only by practical light sources: a glowing {light_source} casting a {color} pool of light on the {surface}. Deep, crushed blacks, moody cinematic teal-and-orange color grading.

**Params**: `aspect_ratio: "16:9"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## drone_aerial

**Prompt**: Drone aerial photography looking straight down at {location}. The composition focuses on the stark, abstract geometric patterns formed by {element_1} contrasting with {element_2}. The lighting is low-angle 'golden hour' sunlight, creating long, dramatic, stretching shadows that emphasize the topography and textures of the ground.

**Params**: `aspect_ratio: "4:5"` · `image_size: "4K"` · `response_modalities: ["IMAGE"]`

## stylized_3d_render

**Prompt**: A hyper-realistic 3D render of a cute, stylized {subject} made of {material}. Rendered in Unreal Engine 5 with subsurface scattering making the material look soft and slightly translucent. Studio lighting with a {rim_light_color} rim light and a {glow_color} ambient glow. The character is placed against an infinite cyclorama background.

**Params**: `aspect_ratio: "1:1"` · `image_size: "2K"` · `response_modalities: ["IMAGE"]`

## sem_microscopy

**Prompt**: Scanning Electron Microscope (SEM) style image of {subject}. False-color imaging using a palette of {color_1} and {color_2}. Extreme magnification revealing alien-like, repeating geometric structures, sharp jagged edges, and deep porous cavities. High contrast, highly scientific and clinical aesthetic.

**Params**: `aspect_ratio: "1:1"` · `image_size: "2K"` · `response_modalities: ["IMAGE"]`

## double_exposure

**Prompt**: Double exposure photographic art. The primary silhouette is a {primary_subject}, filled entirely with a secondary image of {secondary_scene}. The edges of the silhouette softly blend into a {background_color} background. High contrast, ethereal, moody, with the textures of the {secondary_scene} interacting flawlessly with the contours of the {primary_subject}.

**Params**: `aspect_ratio: "2:3"` · `image_size: "2K"` · `response_modalities: ["IMAGE"]`

## architectural_viz

**Prompt**: Architectural Visualization of a {structure} in {style} style. Materials: {materials}. Surrounding landscape: {landscape}. Time of day: {time_of_day}. Lighting: Primary light source from the sun, accurate ray-traced reflections on glass and water surfaces. Camera: Two-point perspective, low angle, tilt-shift lens for vertical correction.

**Params**: `aspect_ratio: "3:2"` · `image_size: "4K"` · `response_modalities: ["TEXT","IMAGE"]`

## isometric_illustration

**Prompt**: Isometric 3D Illustration of {location}. Aesthetic: {aesthetic}. Color palette: {colors}. Activity: {activity}. Lighting: Global illumination, soft ambient occlusion, orthographic camera projection. Background: Solid neutral color, isolated object.

**Params**: `aspect_ratio: "1:1"` · `image_size: "2K"` · `response_modalities: ["IMAGE"]`

## food_photography

**Prompt**: Food Photography of {dish}. Plating: {plating_style} on a {surface_material} surface. Lighting: Backlit with a large diffuser, creating specular highlights on the glossy parts of the food. Vibe: {vibe}. Camera: 105mm macro lens at a 45-degree angle.

**Params**: `aspect_ratio: "4:5"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## motion_blur

**Prompt**: In-Camera Motion Blur Sequence of {subject} performing {action}. Technique: Slow shutter (1/15th sec) with rear-curtain sync strobe flash. Visual Result: The subject's core is frozen and sharp, while the movement drags into a smooth, smeared trail of {blur_color} light. Setting: {background}.

**Params**: `aspect_ratio: "16:9"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## typography_physical

**Prompt**: Typography embedded into physical environment. Text: '{text}'. Environment: {location}. Integration: The text is constructed out of {material}. Lighting: The text interacts with the environment's light, casting accurate shadows onto nearby surfaces. Camera: Eye-level, wide angle, high dynamic range.

**Params**: `aspect_ratio: "16:9"` · `image_size: "4K"` · `response_modalities: ["IMAGE"]`

## retro_futurism

**Prompt**: Retro-Futurism / Analog Sci-Fi depiction of {device}. Design Language: {style}. Features: chunky buttons, CRT screens, scratched paint, dust in crevices. Lighting: Harsh fluorescent overhead lighting, glowing {glow_color} LED indicators. Camera: Polaroid SX-70 emulation, slightly soft focus, muted contrast.

**Params**: `aspect_ratio: "4:3"` · `image_size: "2K"` · `response_modalities: ["IMAGE"]`

## surreal_dreamscape

**Prompt**: Surrealism / Dreamscape art of an ordinary {object}. Surreal Twist: The object is {twist}. Environment: {location}. Physics: Defying gravity, floating elements. Lighting: Ethereal, omnidirectional soft light with no visible source. Color Grading: Pastel tones, low contrast, hazy atmosphere.

**Params**: `aspect_ratio: "1:1"` · `image_size: "2K"` · `response_modalities: ["IMAGE"]`

## character_sheet

**Prompt**: Character Concept Art Sheet of {character}. Features: {features}. Outfit: {clothing}. Layout: A-Pose front, 3/4 profile, and action pose. Background: Neutral medium gray. Rendering Style: Clean line art with flat cel-shading, concept art industry standard.

**Params**: `aspect_ratio: "3:2"` · `image_size: "4K"` · `response_modalities: ["IMAGE"]`

## pbr_texture

**Prompt**: Seamless PBR texture map visualization of {material_type}. Details: {micro_structure}. Imperfections: {imperfections}. Lighting: Raking side light to emphasize normal map depth and bump. Composition: Flat 2D plane facing the camera filling the entire frame.

**Params**: `aspect_ratio: "1:1"` · `image_size: "2K"` · `response_modalities: ["IMAGE"]`

## historical_photo

**Prompt**: Historical Period Piece Photography of {subject} in the era of {era}. Location: {location}. Lighting: Natural light mimicking candlelight. Post-Processing: {film_emulation} emulation, heavy optical vignetting, period-accurate props and costumes.

**Params**: `aspect_ratio: "4:5"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## bioluminescent_nature

**Prompt**: Bioluminescent Nature Macro of {subject}. Modifications: Emitting a natural, glowing {glow_color} bioluminescence. Environment: {location}. Background: Pitch black with faint out-of-focus glowing particles. Camera: Extreme Macro, long exposure feel, high ISO grain.

**Params**: `aspect_ratio: "1:1"` · `image_size: "2K"` · `response_modalities: ["TEXT","IMAGE"]`

## silhouette_shot

**Prompt**: Cinematic Silhouette Master Shot of {subject} performing {action}. Background Focal Point: Massive {focal_point}, extremely bright. Lighting: Pure black silhouette, absolutely zero fill light, heavy back-lit fog wrapping around the subject's edges. Camera: Ultra-wide cinematic aspect ratio (2.35:1), deep depth of field.

**Params**: `aspect_ratio: "21:9"` · `image_size: "4K"` · `response_modalities: ["TEXT","IMAGE"]`
