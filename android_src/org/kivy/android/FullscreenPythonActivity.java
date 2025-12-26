package org.kivy.android;

import android.os.Build;
import android.os.Bundle;
import android.view.Window;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.view.View;
import android.view.ViewGroup;

/**
 * Custom PythonActivity that forces fullscreen mode
 * Compatible with Android 11+ (API 30+) including Android 14+ (API 34+)
 */
public class FullscreenPythonActivity extends PythonActivity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Force fullscreen BEFORE calling super.onCreate
        // This must happen before the window is created
        Window window = getWindow();
        
        // Clear any windowed mode flags
        window.clearFlags(WindowManager.LayoutParams.FLAG_FORCE_NOT_FULLSCREEN);
        
        // Set fullscreen flags
        window.setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN |
            WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN |
            WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            WindowManager.LayoutParams.FLAG_FULLSCREEN |
            WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN |
            WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS
        );
        
        // Set window layout params to fill screen
        WindowManager.LayoutParams params = window.getAttributes();
        params.width = WindowManager.LayoutParams.MATCH_PARENT;
        params.height = WindowManager.LayoutParams.MATCH_PARENT;
        params.x = 0;
        params.y = 0;
        window.setAttributes(params);
        
        // Call super AFTER setting fullscreen
        super.onCreate(savedInstanceState);
        
        // Apply fullscreen using appropriate API for Android version
        applyFullscreen();
    }
    
    private void applyFullscreen() {
        Window window = getWindow();
        View decorView = window.getDecorView();
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // Android 11+ (API 30+) - Use WindowInsetsController
            WindowInsetsController controller = decorView.getWindowInsetsController();
            if (controller != null) {
                controller.hide(android.view.WindowInsets.Type.statusBars() | 
                              android.view.WindowInsets.Type.navigationBars());
                controller.setSystemBarsBehavior(
                    WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
                );
            }
        } else {
            // Android 10 and below - Use deprecated SystemUiVisibility
            decorView.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN |
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            );
        }
        
        // Ensure content view fills screen
        View contentView = findViewById(android.R.id.content);
        if (contentView != null) {
            ViewGroup.LayoutParams layoutParams = contentView.getLayoutParams();
            if (layoutParams != null) {
                layoutParams.width = ViewGroup.LayoutParams.MATCH_PARENT;
                layoutParams.height = ViewGroup.LayoutParams.MATCH_PARENT;
                contentView.setLayoutParams(layoutParams);
            }
        }
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        applyFullscreen();
    }
    
    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            applyFullscreen();
        }
    }
    
    @Override
    protected void onStart() {
        super.onStart();
        applyFullscreen();
    }
}

