#version 300 es
// A green P1 tube over the whole screen: every colour becomes phosphor brightness, glass slightly bowed,
// scanlines, a little halo and darker corners. Toggle with scripts/crt.sh (Super+Shift+C).
precision highp float;
in vec2 v_texcoord;
uniform sampler2D tex;
out vec4 fragColor;
#ifdef GLITCH
uniform float time;

float random(float x) {
    return fract(sin(x * 12.9898) * 43758.5453);
}
#endif

const float BOW = 0.036;              // barrel distortion of the glass
const vec3 PHOSPHOR = vec3(0.20, 1.0, 0.30);

// Brightness the electron beam gets from a pixel: weighted towards green, because that is what P1 phosphor shows.
// The curve lifts the dim greens (muted text, borders) that a plain luma left almost black.
float luma(vec2 uv) {
    float l = dot(texture(tex, uv).rgb, vec3(0.22, 0.62, 0.16));
    return pow(l, 0.78);
}

void main() {
    vec2 size = vec2(textureSize(tex, 0));
    vec2 c = v_texcoord * 2.0 - 1.0;
    // normalised at the middle of each side: the picture stays inside the glass and only the corners go black
    c *= (1.0 + BOW * dot(c, c)) / (1.0 + BOW);
    vec2 uv = c * 0.5 + 0.5;
#ifdef GLITCH  // the picture loses sync: bands slip sideways and the frame rolls (scripts/glitch.py)
    float tick = floor(time * 30.0);
    float band = floor(v_texcoord.y * 18.0);
    uv.x += step(0.62, random(band + tick)) * (random(tick + 7.0) - 0.5) * 0.16;
    uv.y = fract(uv.y + (random(tick + 3.0) - 0.5) * 0.05);
#endif

    vec2 px = 1.6 / size, far = 4.0 / size;
    float halo = (luma(uv + vec2(px.x, 0.0)) + luma(uv - vec2(px.x, 0.0))
                + luma(uv + vec2(0.0, px.y)) + luma(uv - vec2(0.0, px.y))) * 0.25;
    float glow = (luma(uv + far) + luma(uv - far)
                + luma(uv + vec2(far.x, -far.y)) + luma(uv - vec2(far.x, -far.y))) * 0.25;
    float v = luma(uv) * 0.9 + halo * 0.15 + glow * 0.12;

    // Raster lines: the beam is thicker where it is brighter, so bright text fills the gaps and only dim areas show them.
    float line = 0.5 + 0.5 * sin(v_texcoord.y * size.y * 2.0944);       // one dark line every 3 pixels
    float scan = 1.0 - line * mix(0.8, 0.35, clamp(v, 0.0, 1.0));
    float mask = 0.78 + 0.22 * sin(v_texcoord.x * size.x * 2.0944);     // faint phosphor stripes
    float vignette = 1.0 - 0.4 * pow(dot(c, c) * 0.5, 1.4);
    vec2 edge = smoothstep(vec2(1.0), vec2(0.985), abs(c));          // soft edge of the tube
    vec3 lit = PHOSPHOR * v * scan * mask * 1.5;
    lit = 1.0 - exp(-lit * 1.4);                                         // soft clip instead of a hard white-out
    // A real tube is never pure black: the raster and the glass glow faintly, brightest in the middle.
    vec3 haze = vec3(0.002, 0.016, 0.006) * (1.0 - 0.6 * dot(c, c) * 0.5);
    fragColor = vec4((lit + haze) * vignette * edge.x * edge.y, 1.0);
}
