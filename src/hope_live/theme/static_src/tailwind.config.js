module.exports = {
    content: [
        // Templates within theme app (e.g. base.html)
        '../templates/**/*.html',
        // Templates in other apps
        '../../templates/**/*.html',
        '../../../templates/**/*.html',
        // // Ignore files in node_modules
        // '!../../**/node_modules',
        // // Include JavaScript files that might contain Tailwind CSS classes
        // '../../**/*.js',
        // Include Python files that might contain Tailwind CSS classes
        '../../../**/*.py'
    ],
    theme: {
        extend: {
            // your customizations
        },
    },
    plugins: [
        "postcss-import",
        require('daisyui'),
        "@tailwindcss/postcss"
        // any other Tailwind plugin you need
    ],
    daisyui: {
        themes: [{
            light: {
                "primary": "193 100% 47%",      // UNICEF Blue
                "secondary": "217 45% 20%",     // UNICEF Dark Blue
                "accent": "193 80% 55%",
                "neutral": "217 45% 20%",
                "base-100": "0 0% 100%",         // White background
                "base-content": "217 45% 20%",  // Dark Blue text
                "info": "198 93% 60%",
                "success": "145 63% 49%",
                "warning": "43 96% 56%",
                "error": "0 84% 60%",
            },
        },
            {
                dark: {
                    "primary": "193 100% 47%",      // UNICEF Blue (vibrant on dark)
                    "secondary": "217 30% 35%",     // Lighter shade of the dark blue
                    "accent": "193 80% 55%",
                    "neutral": "217 30% 35%",
                    "base-100": "217 45% 20%",     // UNICEF Dark Blue for background
                    "base-content": "210 17% 82%", // Light, soft text color
                    "info": "198 93% 60%",
                    "success": "145 63% 49%",
                    "warning": "43 96% 56%",
                    "error": "0 84% 60%",
                },
            },
        ],  // pick which ones you want
        // other daisyUI config if needed
    },
}
