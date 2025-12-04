#version 330 core

out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D sceneTexture;
uniform sampler2D bloomTexture; // Optional if we do bloom separate
uniform bool useBloom;
uniform bool useVignette;
uniform bool useChromaticAberration;
uniform bool useFXAA; // Placeholder for now, FXAA usually needs its own pass or complex logic

// Vignette Settings
const float vignetteIntensity = 0.1;
const float vignetteSmoothness = 0.3;

// Chromatic Aberration Settings
const float chromaticOffset = 0.0008;

void main()
{
    vec2 uv = TexCoords;
    vec3 color = texture(sceneTexture, uv).rgb;
    
    // Chromatic Aberration
    if (useChromaticAberration) {
        float r = texture(sceneTexture, uv + vec2(chromaticOffset, 0.0)).r;
        float b = texture(sceneTexture, uv - vec2(chromaticOffset, 0.0)).b;
        color.r = r;
        color.b = b;
    }
    
    // Bloom Combine (Simple Additive)
    if (useBloom) {
        vec3 bloomColor = texture(bloomTexture, uv).rgb;
        color += bloomColor * 1.5; // Boost bloom intensity
    }
    
    // Vignette
    if (useVignette) {
        vec2 center = vec2(0.5, 0.5);
        float dist = distance(uv, center);
        float vignette = smoothstep(0.8, 0.8 - vignetteSmoothness, dist * (1.0 + vignetteIntensity));
        color *= vignette;
    }
    
    // Tone Mapping & Gamma Correction - DISABLED (Causing white screen/washout)
    // color = color / (color + vec3(1.0));
    // color = pow(color, vec3(1.0 / 2.2));
    
    FragColor = vec4(color, 1.0);
}
