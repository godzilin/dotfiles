#version 300 es
// A green P1 tube over the whole screen: every colour becomes phosphor brightness, glass slightly bowed,
// scanlines, a little halo and darker corners. Toggle with scripts/crt.sh (Super+Shift+C).
precision highp float;
in vec2 v_texcoord;
uniform sampler2D tex;
out vec4 fragColor;

const float BOW = 0.012;              // barrel distortion of the glass: more blurs small text
const vec3 PHOSPHOR = vec3(0.20, 1.0, 0.30);

float luma(vec2 uv) {
    return dot(texture(tex, uv).rgb, vec3(0.299, 0.587, 0.114));
}

void main() {
    vec2 size = vec2(textureSize(tex, 0));
    vec2 c = v_texcoord * 2.0 - 1.0;
    // normalised at the middle of each side: the picture stays inside the glass and only the corners go black
    c *= (1.0 + BOW * dot(c, c)) / (1.0 + BOW);
    vec2 uv = c * 0.5 + 0.5;

    vec2 px = 1.6 / size;
    float halo = (luma(uv + vec2(px.x, 0.0)) + luma(uv - vec2(px.x, 0.0))
                + luma(uv + vec2(0.0, px.y)) + luma(uv - vec2(0.0, px.y))) * 0.25;
    float v = luma(uv) * 0.85 + halo * 0.3;

    float scan = 0.86 + 0.14 * sin(v_texcoord.y * size.y * 2.0944); // one dark line every 3 pixels
    float vignette = 1.0 - 0.28 * pow(dot(c, c) * 0.5, 1.5);
    vec2 edge = smoothstep(vec2(1.0), vec2(0.985), abs(c));          // soft edge of the tube
    fragColor = vec4(PHOSPHOR * v * scan * vignette * edge.x * edge.y * 1.12 + vec3(0.0, 0.012, 0.004), 1.0);
}
