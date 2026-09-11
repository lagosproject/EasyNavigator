# Add project specific ProGuard rules here.
-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# ZXing rules
-keep class com.google.zxing.** { *; }
-dontwarn com.google.zxing.**
