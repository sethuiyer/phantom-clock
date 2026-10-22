--  Exhaustive runtime test for the parameterized encoder.
--
--  SPARK_Mode is Off: this driver EXECUTES the contracts as run-time checks
--  rather than proving them, and it tests several distinct table shapes,
--  including the degenerate single-chart table (K_Max = 0) that the released
--  three-entry specification could not express.

with Ada.Text_IO; use Ada.Text_IO;
with General_Chart_Encoder; use General_Chart_Encoder;

procedure Test_General is

   Failures : Natural := 0;

   procedure Check (OK : Boolean; What : String) is
   begin
      if not OK then
         Failures := Failures + 1;
         Put_Line ("  FAIL: " & What);
      end if;
   end Check;

   --  Exhaustively verify bijectivity and the round trip for one table.
   procedure Verify (Name : String; T : Chart_Table) is
      Seen  : array (Address) of Boolean := (others => False);
      Count : Natural := 0;
      A     : Address;
      K     : Chart_Id;
      R     : Arena_Bound;
   begin
      Check (Is_Consistent (T), Name & ": table is consistent");

      for C in 0 .. T.K_Max loop
         for I in 0 .. T.Cells (C) - 1 loop
            declare
               Enc : constant Address := Encode (T, C, I);
            begin
               Check (not Seen (Enc), Name & ": no address aliasing");
               Check (Arena_Bound (Enc) < T.Arena_Size, Name & ": address in arena");
               Seen (Enc) := True;
               Count := Count + 1;
            end;
         end loop;
      end loop;

      Check (Count = Natural (T.Arena_Size), Name & ": every address produced once");

      A := 0;
      while A < Address (T.Arena_Size) loop
         Check (Seen (A), Name & ": arena fully covered");
         A := A + 1;
      end loop;

      --  Round trip.
      for C in 0 .. T.K_Max loop
         for I in 0 .. T.Cells (C) - 1 loop
            declare
               Enc : constant Address := Encode (T, C, I);
            begin
               Decode (T, Enc, K, R);
               Check (K = C and then R = I, Name & ": decode inverts encode");
            end;
         end loop;
      end loop;
   end Verify;

   --  (0,512) (512,256) (768,256) -- the released Experiment 4 table.
   T_Released : constant Chart_Table :=
     (K_Max => 2, Arena_Size => 1024,
      Base  => (0, 512, 768),
      Cells => (512, 256, 256));

   --  Single chart: K_Max = 0, the degenerate case that used to underflow.
   T_Single : constant Chart_Table :=
     (K_Max => 0, Arena_Size => 4096,
      Base  => (0 => 0),
      Cells => (0 => 4096));

   --  Four unequal charts, exercising a non-power-of-two count.
   T_Four : constant Chart_Table :=
     (K_Max => 3, Arena_Size => 1000,
      Base  => (0, 7, 500, 999),
      Cells => (7, 493, 499, 1));

   --  A larger table: 8 charts of 1000 each.
   T_Eight : constant Chart_Table :=
     (K_Max => 7, Arena_Size => 8000,
      Base  => (0, 1_000, 2_000, 3_000, 4_000, 5_000, 6_000, 7_000),
      Cells => (1_000, 1_000, 1_000, 1_000, 1_000, 1_000, 1_000, 1_000));

begin
   Put_Line ("general_chart_encoder: exhaustive verification");

   Verify ("released(3)", T_Released);
   Verify ("single(1)  ", T_Single);
   Verify ("four(4)    ", T_Four);
   Verify ("eight(8)   ", T_Eight);

   --  Inconsistent tables must be rejected by the predicate itself.
   Check (not Is_Consistent
            ((K_Max => 1, Arena_Size => 100, Base => (0, 70), Cells => (60, 30))),
          "gap between intervals is rejected");
   Check (not Is_Consistent
            ((K_Max => 1, Arena_Size => 100, Base => (0, 50), Cells => (60, 50))),
          "overlapping intervals are rejected");
   Check (not Is_Consistent
            ((K_Max => 1, Arena_Size => 100, Base => (0, 50), Cells => (50, 49))),
          "short tiling is rejected");
   Check (not Is_Consistent
            ((K_Max => 1, Arena_Size => 100, Base => (5, 50), Cells => (50, 50))),
          "nonzero origin is rejected");
   Check (not Is_Consistent
            ((K_Max => 1, Arena_Size => 100, Base => (0, 50), Cells => (50, 0))),
          "empty chart is rejected");

   if Failures = 0 then
      Put_Line ("PASS: all checks passed on 4 tables, 5 negative controls");
   else
      Put_Line ("FAILURES:" & Natural'Image (Failures));
   end if;
end Test_General;
