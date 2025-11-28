#version 120

uniform float time;
uniform vec2 resolution;

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
    float angle = atan(uv.y, uv.x);
    float radius = length(uv);
    
    vec3 col = vec3(0.0); // Black background
    float speed = 1.5;
    float t = time * speed;
    
    // --- Nebula Layer ---
    // --- Nebula Layer ---
    // Twist the nebula with the warp
    // Use cylindrical coordinates for noise to avoid seam at angle wrap
    float noise_r = 2.0;
    // We move along Z (time) and twist angle with radius
    float twist = radius * 2.0;
    vec3 noisePos = vec3(cos(angle + twist) * noise_r, sin(angle + twist) * noise_r, radius * 3.0 - time * 0.5);
    
    float n = fbm(noisePos);
    float n2 = fbm(noisePos * 2.0 + vec3(3.0));
    
    vec3 nebColor1 = vec3(0.1, 0.0, 0.2); // Purple
    vec3 nebColor2 = vec3(0.0, 0.2, 0.4); // Blue
    vec3 nebColor3 = vec3(0.4, 0.1, 0.1); // Reddish
    
    vec3 nebula = mix(nebColor1, nebColor2, n);
    nebula += nebColor3 * pow(n2, 3.0);
    
    // Fade nebula at center to avoid singularity artifacts
    nebula *= smoothstep(0.0, 0.3, radius);
    
    col += nebula;
    
    // --- Warp Stars Layer ---
    // Iterate through layers of "stars"
    for (int i = 0; i < 8; i++) {
        // More sectors = more stars
        float sectors = 40.0 + float(i) * 20.0;
        float id = floor(angle / 6.28318 * sectors);
        
        // Random hash for this sector
        float r_hash = fract(sin(id * 12.9898 + float(i) * 78.233) * 43758.5453);
        
        // Depth of this layer
        // We want them to move FROM center (z=far) TO camera (z=near)
        // Add r_hash to offset to break circle patterns
        float z = 1.0 - fract(t * 0.5 + float(i) * 0.15 + r_hash * 0.8);
        
        // Fade in from center (far) and out at edges (near)
        float fade = smoothstep(1.0, 0.8, z) * smoothstep(0.0, 0.2, z);
        
        // Perspective projection
        float projected_r = 0.1 / max(z, 0.001);
        
        // Only some sectors have stars
        if (r_hash > 0.75) { // Increased probability
            float center_angle = (id + 0.5) / sectors * 6.28318;
            float diff = abs(angle - center_angle);
            if (diff > 3.14159) diff = 6.28318 - diff;
            
            float width = 0.015; // Slightly thicker
            float streak_intensity = smoothstep(width, 0.0, diff);
            
            float trail = smoothstep(projected_r - 0.5, projected_r, radius);
            // And clip at projected_r (head)
            float head = smoothstep(projected_r + 0.1, projected_r, radius);
            
            // Combine
            float ray = streak_intensity * trail * head;
            
            // Color
            vec3 streakCol = vec3(0.2, 0.5, 1.0); // Deep Blue
            if (r_hash > 0.9) streakCol = vec3(0.8, 0.9, 1.0); // White/Blue
            
            col += streakCol * ray * fade * (1.0/z);
        }
    }
    
    // Vignette / Center darkness
    col *= smoothstep(0.0, 0.4, radius);
    
    gl_FragColor = vec4(col, 1.0);
}
