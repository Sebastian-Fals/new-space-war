#version 120

uniform float time;
uniform vec2 resolution;
uniform vec2 player_pos;

varying vec2 v_texcoord;

// Rotation matrix for Y-axis (Yaw)
mat3 rotateY(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat3(
        c, 0.0, -s,
        0.0, 1.0, 0.0,
        s, 0.0, c
    );
}

// Rotation matrix for X-axis (Pitch)
mat3 rotateX(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat3(
        1.0, 0.0, 0.0,
        0.0, c, -s,
        0.0, s, c
    );
}

// Random hash function
float hash(float n) {
    return fract(sin(n) * 43758.5453123);
}

// 3D Noise function
float noise(vec3 x) {
    vec3 p = floor(x);
    vec3 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);
    float n = p.x + p.y * 57.0 + 113.0 * p.z;
    return mix(mix(mix(hash(n + 0.0), hash(n + 1.0), f.x),
                   mix(hash(n + 57.0), hash(n + 58.0), f.x), f.y),
               mix(mix(hash(n + 113.0), hash(n + 114.0), f.x),
                   mix(hash(n + 170.0), hash(n + 171.0), f.x), f.y), f.z);
}

// Fractal Brownian Motion
float fbm(vec3 p) {
    float f = 0.0;
    f += 0.5000 * noise(p); p = p * 2.02;
    f += 0.2500 * noise(p); p = p * 2.03;
    f += 0.1250 * noise(p); p = p * 2.01;
    f += 0.0625 * noise(p);
    return f;
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * resolution.xy) / resolution.y;
    
    // Camera Rotation based on player position
    // Map player X to Yaw, Player Y to Pitch
    float yaw = player_pos.x * 0.0005; 
    float pitch = player_pos.y * 0.0005;
    
    // Ray direction
    vec3 ro = vec3(0.0, 0.0, time * 2.0); // Move forward over time
    vec3 rd = normalize(vec3(uv, 1.0));
    
    // Apply rotation to ray direction
    rd = rotateY(yaw) * rotateX(pitch) * rd;
    
    vec3 color = vec3(0.0);
    
    // 1. Volumetric Nebula (Raymarching FBM)
    vec3 nebulaPos = rd * 4.0 + vec3(0.0, 0.0, time * 0.5);
    float n = fbm(nebulaPos);
    float n2 = fbm(nebulaPos * 2.0 + vec3(2.0));
    
    vec3 nebulaColor1 = vec3(0.1, 0.0, 0.2); // Deep Purple
    vec3 nebulaColor2 = vec3(0.0, 0.1, 0.3); // Deep Blue
    vec3 nebulaColor3 = vec3(0.5, 0.2, 0.1); // Orange/Red highlights
    
    vec3 nebula = mix(nebulaColor1, nebulaColor2, n);
    nebula += nebulaColor3 * pow(n2, 3.0) * 0.5;
    
    color += nebula * 1.5;
    
    // 2. Starfield (3D Grid)
    // Render stars ON TOP of nebula for visibility
    float starIntensity = 0.0;
    vec3 starColor = vec3(0.0);
    
    // Camera moves forward
    vec3 star_ro = vec3(0.0, 0.0, time * 5.0); 
    
    for (float i = 0.0; i < 20.0; i++) {
        // Position along ray
        float t = i * 1.0 + hash(i) * 0.5; 
        
        // We want to sample the world at this distance
        vec3 p = star_ro + rd * t;
        
        // Map to grid
        vec3 id = floor(p);
        vec3 local = fract(p) - 0.5;
        
        // Random star in this cell?
        float n_star = hash(id.x + id.y * 57.0 + id.z * 113.0);
        
        if (n_star > 0.85) { // Even more stars
            // Reduced Size
            float size = 0.015 + hash(n_star) * 0.03; 
            float dist = length(local);
            
            // Star Core - Sharper falloff, less intense
            float brightness = max(0.0, 1.0 - dist / size);
            brightness = pow(brightness, 3.0); 
            
            // Star Glow (Bloom) - Much subtler
            float glow = max(0.0, 1.0 - dist / (size * 8.0));
            glow = pow(glow, 2.0) * 0.2;
            
            // Star Color - Less saturated, dimmer
            vec3 tint = mix(vec3(0.7, 0.8, 1.0), vec3(1.0, 0.9, 0.8), hash(n_star * 10.0));
            if (hash(n_star * 20.0) > 0.95) tint = vec3(1.0, 0.6, 0.6); // Rare red stars
            
            // Distance fade (Fog)
            float fade = smoothstep(20.0, 10.0, t);
            
            starColor += (brightness + glow) * tint * fade * 0.8;
        }
    }
    color += starColor;
    
    // Vignette
    float vig = 1.0 - length(uv) * 0.5;
    color *= vig;
    
    gl_FragColor = vec4(color, 1.0);
}
