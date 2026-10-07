package io.github.maquekenzhegua.kaoyan;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;

import androidx.core.app.ActivityCompat;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/** JS ↔ 原生桥:持久化倒计时数据、安排提醒闹钟、刷新小组件、请求通知权限。 */
@CapacitorPlugin(name = "NativeBridge")
public class ReminderPlugin extends Plugin {

    @PluginMethod
    public void saveData(PluginCall call) {
        String key = call.getString("key");
        String value = call.getString("value", "");
        if (key == null || key.isEmpty()) {
            call.reject("missing key");
            return;
        }
        getContext().getSharedPreferences(ReminderScheduler.PREF_FILE, Context.MODE_PRIVATE)
                .edit().putString(key, value).apply();
        call.resolve();
    }

    @PluginMethod
    public void refresh(PluginCall call) {
        ReminderScheduler.reschedule(getContext());
        CountdownWidgetProvider.updateAll(getContext());
        call.resolve();
    }

    @PluginMethod
    public void requestNotifPermission(PluginCall call) {
        if (Build.VERSION.SDK_INT >= 33) {
            ActivityCompat.requestPermissions(getActivity(),
                    new String[]{Manifest.permission.POST_NOTIFICATIONS}, 4101);
        }
        call.resolve();
    }
}
