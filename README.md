<span><img src="https://github.com/JimothyJohn/WhataGAN/raw/master/docs/whatagan.png" width="24%">
<img src="https://github.com/JimothyJohn/WhataGAN/raw/master/docs/whatagan.png" width="24%">
<img src="https://github.com/JimothyJohn/WhataGAN/raw/master/docs/whatagan.png" width="24%">
<img src="https://github.com/JimothyJohn/WhataGAN/raw/master/docs/whatagan.png" width="24%"></span>

# WhataGAN

Generate new Whataburger store concepts the likes of which have never been seen!

## Purpose

WhataGAN is an exercise in data collection, organization, refinement, and synthesis.

## Function

After installing and activating the conda environment run:

```bash
python whatagan
```

## Layout

Metadata will be stored in JSON format with the following schema:

```json
{
    // 
    "location": "Whataburger+2424+Baldwin+Blvd,Corpus-Christi,TX",
    // Internal identifier (will be replaced as key by store)
    "uuid": "57e00294bce4451ebf3807747200b911",
    // Whataburger Store #
    "number": 2,
    // Can StreetView see this location?
    "present": false,
    // GAN needs at least 512x512
    "size": "600x600",
    // Orientation range of camera where store can be seen
    "heading": [
        0,
        340
    ],
    // Zoom range of camera where store can be seen
    "fov": [
        80,
        81
    ],
    // Pitch range of camera where store can be seen
    "pitch": [
        10,
        11
    ]
}
```

## To-do

- Incorporate MongoDB for persistent metadata storage
- Add Streamlit UI for easy metadata manipulation
