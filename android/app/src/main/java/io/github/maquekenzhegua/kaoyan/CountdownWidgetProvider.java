package io.github.maquekenzhegua.kaoyan;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.widget.RemoteViews;

import org.json.JSONObject;

/** 桌面小组件:校园照片 + 大红倒计时天数,点击打开 App。 */
public class CountdownWidgetProvider extends AppWidgetProvider {

    @Override
    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {
        updateAll(context);
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        super.onReceive(context, intent);
        updateAll(context);
    }

    static void updateAll(Context context) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(context);
        if (mgr == null) return;
        int[] ids = mgr.getAppWidgetIds(new ComponentName(context, CountdownWidgetProvider.class));
        if (ids.length == 0) return;

        JSONObject d = ReminderScheduler.nativeData(context);
        String file = d.optString("photoFile", "thu-1.jpg");
        String school = d.optString("schoolName", "考研上岸");
        String ky = d.optString("ky", "2028");
        String exam = d.optString("exam", "2027-12-18");
        int days = DayReminderReceiver.daysUntil(exam);
        if (days < 0) days = 0;

        RemoteViews rv = new RemoteViews(context.getPackageName(), R.layout.widget_countdown);
        rv.setTextViewText(R.id.w_days, String.valueOf(days));
        rv.setTextViewText(R.id.w_school, school);
        rv.setTextViewText(R.id.w_kicker, "距 " + ky + " 考研初试还有");
        try {
            BitmapFactory.Options o = new BitmapFactory.Options();
            o.inSampleSize = 2;
            Bitmap bmp = BitmapFactory.decodeStream(
                    context.getAssets().open("public/img/" + file), null, o);
            if (bmp != null) rv.setImageViewBitmap(R.id.w_photo, bmp);
        } catch (Exception ignored) {
        }
        Intent open = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName());
        PendingIntent pi = PendingIntent.getActivity(context, 3001, open,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        rv.setOnClickPendingIntent(R.id.w_root, pi);
        mgr.updateAppWidget(ids, rv);
    }
}
